import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiClient {
  // Backend em produção (Render).
  static const String baseUrl = 'https://rumo-api-5s0b.onrender.com';

  final http.Client _client = http.Client();

  /// Faz o login e retorna o token JWT.
  ///
  /// O backend espera `application/x-www-form-urlencoded` com
  /// `username` (e-mail) e `password`.
  Future<String> login(String email, String password) async {
    final uri = Uri.parse('$baseUrl/auth/login');
    final response = await _client
        .post(
          uri,
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
          body: {'username': email, 'password': password},
        )
        .timeout(const Duration(seconds: 30));

    if (response.statusCode != 200) {
      throw ApiException(
        response.statusCode,
        _extractMessage(response.body) ?? 'Falha no login',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final token = data['access_token'] as String?;
    if (token == null) {
      throw ApiException(500, 'Resposta sem access_token');
    }
    return token;
  }

  /// GET autenticado.
  Future<dynamic> get(String path, {String? token}) async {
    final uri = Uri.parse('$baseUrl$path');
    final headers = <String, String>{'Accept': 'application/json'};
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }

    final response = await _client
        .get(uri, headers: headers)
        .timeout(const Duration(seconds: 30));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(
        response.statusCode,
        _extractMessage(response.body) ?? 'Erro ${response.statusCode}',
      );
    }

    if (response.body.isEmpty) return null;
    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  String? _extractMessage(String body) {
    if (body.isEmpty) return null;
    try {
      final data = jsonDecode(body);
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
    } catch (_) {
      // corpo não é JSON
    }
    return body;
  }
}