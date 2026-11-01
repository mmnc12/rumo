import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'api.dart';

class AuthService extends ChangeNotifier {
  static const _tokenKey = 'rumo.token';

  final ApiClient _api = ApiClient();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  String? _token;
  bool _loading = true;

  String? get token => _token;
  bool get isLoggedIn => _token != null;
  bool get loading => _loading;

  ApiClient get api => _api;

  /// Carrega o token salvo no início do app.
  Future<void> bootstrap() async {
    _token = await _storage.read(key: _tokenKey);
    _loading = false;
    notifyListeners();
  }

  /// Faz login, salva o token e notifica a UI.
  Future<void> login(String email, String password) async {
    final token = await _api.login(email, password);
    _token = token;
    await _storage.write(key: _tokenKey, value: token);
    notifyListeners();
  }

  /// Remove o token (logout).
  Future<void> logout() async {
    _token = null;
    await _storage.delete(key: _tokenKey);
    notifyListeners();
  }
}