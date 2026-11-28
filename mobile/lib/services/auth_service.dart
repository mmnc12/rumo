import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'api.dart';

class AuthService extends ChangeNotifier {
  static const _tokenKey = 'rumo.token';

  final ApiClient _api = ApiClient();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  String? _token;
  bool _loading = true;

  // [Sessão 10] Cache do id do usuário extraído do JWT.
  // Decodificado uma vez quando o token muda, não a cada build().
  String? _cachedUserId;

  String? get token => _token;
  bool get isLoggedIn => _token != null;
  bool get loading => _loading;

  ApiClient get api => _api;

  /// [Sessão 51 — item 10.4 Onda B] Construtor explícito para injetar o
  /// callback de 401 no ApiClient. O corpo do construtor roda DEPOIS da
  /// inicialização dos campos, então `_api` já existe quando setamos o
  /// callback. O ApiClient NÃO conhece AuthService — só chama a função.
  AuthService() {
    _api.onUnauthorized = _handleUnauthorized;
  }

  /// [Sessão 51 — item 10.4 Onda B] Chamado pelo ApiClient quando uma
  /// chamada AUTENTICADA recebe 401 (token expirado/inválido).
  ///
  /// Guard `isLoggedIn`: idempotente — se duas chamadas 401 chegarem
  /// juntas, a segunda não faz nada (o token já foi limpo pela primeira).
  /// Evita loop e logout duplicado.
  ///
  /// Só faz logout. A navegação para /login é consequência do
  /// `refreshListenable: _auth` no GoRouter (main.dart): `logout()`
  /// chama `notifyListeners()`, o GoRouter reavalia o redirect e, como
  /// `!isLoggedIn && !authPage`, manda para /login. Sem esse
  /// refreshListenable, o logout não navegaria (a rota não mudou).
  void _handleUnauthorized() {
    if (!isLoggedIn) return;
    // ignore: discarded_futures — logout() é async mas o callback é sync.
    // O AuthService não tem como aguardar aqui; a UI reage via
    // notifyListeners() (loading/token) e o redirect do GoRouter.
    logout();
  }

  /// Id do usuário autenticado (claim `sub` do JWT; fallback `user_id`).
  ///
  /// Retorna `null` quando não há token, quando o token é malformado ou
  /// quando o payload não traz `sub`/`user_id`. Nunca lança — quem chama
  /// só precisa tratar o caso "sem id" (esconde botões que dependem do
  /// usuário atual, como o de excluir comentário).
  ///
  /// Fonte única de verdade para o id do usuário no app: o detalhe da
  /// atividade, o feed e qualquer tela futura que precise comparar com
  /// `comment.user_id` / `activity.user_id` deve usar este getter em vez
  /// de decodificar o JWT localmente.
  String? get currentUserId => _cachedUserId;

  /// Define o token e invalida o cache do id do usuário.
  void _setToken(String? token) {
    _token = token;
    _cachedUserId = token == null ? null : _decodeUserId(token);
  }

  /// Decodifica o payload do JWT e extrai `sub` (fallback `user_id`).
  static String? _decodeUserId(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;
      final normalized = base64Url.normalize(parts[1]);
      final decoded = utf8.decode(base64Url.decode(normalized));
      final data = jsonDecode(decoded);
      if (data is Map<String, dynamic>) {
        final sub = data['sub'];
        if (sub is String) return sub;
        final userId = data['user_id'];
        if (userId is String) return userId;
      }
    } catch (_) {
      // token inválido/expirado — sem id.
    }
    return null;
  }

  /// Carrega o token salvo no início do app.
  Future<void> bootstrap() async {
    _setToken(await _storage.read(key: _tokenKey));
    _loading = false;
    notifyListeners();
  }

  /// Faz login, salva o token e notifica a UI.
  Future<void> login(String email, String password) async {
    final token = await _api.login(email, password);
    _setToken(token);
    await _storage.write(key: _tokenKey, value: token);
    notifyListeners();
  }

  /// [Sessão 49 — item 10.2] Cadastra um novo usuário e faz login automático.
  ///
  /// Fluxo:
  /// 1. `POST /auth/register` (público) — cria o usuário.
  /// 2. Em seguida, `POST /auth/login` com as mesmas credenciais.
  /// 3. Salva o token e notifica a UI (mesma semântica de `login`).
  ///
  /// Erros:
  /// - 409 do register propaga como `ApiException` (o caller trata o
  ///   `e.message` — S48d — porque email e username têm `detail` diferentes).
  /// - 401 do login só aconteceria se o register tivesse sucesso e o login
  ///   falhasse por algum motivo estranho (não deveria — mesmas credenciais).
  Future<void> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
    double? weightKg,
    double? heightCm,
    String? birthDate,
  }) async {
    // 1) Cria o usuário. Se der erro (409/422/429), propaga para o caller.
    await _api.register(
      email: email,
      username: username,
      password: password,
      fullName: fullName,
      weightKg: weightKg,
      heightCm: heightCm,
      birthDate: birthDate,
    );

    // 2) Login automático com as credenciais recém-cadastradas.
    //    Reusa o mesmo caminho do login normal (POST /auth/login).
    await login(email, password);
  }

  /// Remove o token (logout).
  Future<void> logout() async {
    _setToken(null);
    await _storage.delete(key: _tokenKey);
    notifyListeners();
  }
}