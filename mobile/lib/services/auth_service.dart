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

  /// Remove o token (logout).
  Future<void> logout() async {
    _setToken(null);
    await _storage.delete(key: _tokenKey);
    notifyListeners();
  }
}