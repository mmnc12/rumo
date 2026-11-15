import 'dart:convert';
import 'dart:io'; // [Sessão 31] File para upload multipart
import 'package:http/http.dart' as http;

import '../models/activity.dart'; // [Sessão 31] Activity.fromJson no retorno do upload
import '../models/activity_track.dart';
import '../models/comment.dart';

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
    final response = await _send('GET', path, token: token);
    return _decode(response);
  }

  /// POST autenticado. `body` é serializado como JSON.
  Future<dynamic> post(
    String path, {
    Object? body,
    String? token,
  }) async {
    final response = await _send('POST', path, token: token, body: body);
    return _decode(response);
  }

  /// DELETE autenticado.
  Future<dynamic> delete(String path, {String? token}) async {
    final response = await _send('DELETE', path, token: token);
    return _decode(response);
  }

  // ---------- Upload (Sessão 31) ----------

  /// Envia um arquivo GPX ou FIT para `POST /activities/upload`.
  ///
  /// O backend (FastAPI) espera `multipart/form-data` com:
  /// - `file` (obrigatório): .gpx ou .fit
  /// - `title` (opcional, maxLength 120)
  /// - `activity_type` (opcional; o backend valida o enum)
  /// - `description` (opcional)
  ///
  /// Sucesso: 201 com `ActivityResponse` (parseado por `Activity.fromJson`).
  /// Erro: `ApiException` com o `.detail` do FastAPI (422/429/etc).
  ///
  /// [Sessão 31 — fix] Aceita DOIS caminhos:
  /// - `file` (File, Android/iOS/Desktop): usa `MultipartFile.fromPath`
  /// - `bytes` + `filename` (Web): usa `MultipartFile.fromBytes`
  /// Na web o `file_picker` NÃO expõe `path` (sempre null); só bytes.
  ///
  /// NOTA: NÃO usa `_send` porque `_send` é JSON-only. Multipart tem
  /// contrato próprio (headers gerados pelo `MultipartRequest`, body
  /// binário). Os endpoints existentes ficam intocados.
  Future<Activity> uploadActivity({
    File? file,
    List<int>? bytes,
    String? filename,
    String? title,
    String? activityType,
    String? description,
    String? token,
  }) async {
    if (file == null && bytes == null) {
      throw ApiException(400, 'Nenhum arquivo para upload.');
    }

    final uri = Uri.parse('$baseUrl/activities/upload');
    final request = http.MultipartRequest('POST', uri);

    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    request.headers['Accept'] = 'application/json';

    if (file != null) {
      request.files.add(
        await http.MultipartFile.fromPath('file', file.path),
      );
    } else {
      // Web: bytes em memória + filename.
      final name = (filename == null || filename.isEmpty)
          ? 'upload.gpx'
          : filename;
      request.files.add(
        http.MultipartFile.fromBytes('file', bytes!, filename: name),
      );
    }

    if (title != null && title.trim().isNotEmpty) {
      request.fields['title'] = title.trim();
    }
    if (activityType != null && activityType.trim().isNotEmpty) {
      request.fields['activity_type'] = activityType.trim();
    }
    if (description != null && description.trim().isNotEmpty) {
      request.fields['description'] = description.trim();
    }

    late final http.StreamedResponse streamed;
    try {
      streamed = await _client.send(request).timeout(
            const Duration(seconds: 60),
          );
    } catch (e) {
      // Timeout / rede / DNS — o upload é síncrono no backend (~1-3s).
      throw ApiException(0, 'Falha de rede no upload: $e');
    }

    final response = await http.Response.fromStream(streamed);

    if (response.statusCode != 201) {
      throw ApiException(
        response.statusCode,
        _extractMessage(response.body) ?? 'Falha no upload',
      );
    }

    final data = jsonDecode(utf8.decode(response.bodyBytes));
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada do upload');
    }
    return Activity.fromJson(data);
  }

  // ---------- Comentários ----------

  /// Lista os comentários de uma atividade (ordem cronológica, conforme backend).
  Future<List<Comment>> listComments(
    String activityId, {
    String? token,
  }) async {
    final data = await get('/activities/$activityId/comments', token: token);
    if (data is! List) {
      throw ApiException(500, 'Resposta inesperada ao listar comentários');
    }
    return data
        .map((e) => Comment.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Cria um comentário na atividade e retorna o comentário criado.
  Future<Comment> createComment(
    String activityId,
    String content, {
    String? token,
  }) async {
    final data = await post(
      '/activities/$activityId/comments',
      body: {'content': content},
      token: token,
    );
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada ao criar comentário');
    }
    return Comment.fromJson(data);
  }

  /// Deleta um comentário (somente o autor; o backend valida).
  Future<void> deleteComment(String commentId, {String? token}) async {
    await delete('/comments/$commentId', token: token);
  }

  // ---------- Rota (track) ----------

  /// Busca a geometria da rota da atividade.
  ///
  /// Retorna `null` quando o backend responde 404 ("Atividade não possui
  /// rota") — nesse caso o detalhe simplesmente esconde o card de mapa.
  /// Qualquer outro erro (401, 403, 500, timeout) propaga como `ApiException`.
  Future<ActivityTrack?> getActivityTrack(
    String activityId, {
    String? token,
  }) async {
    try {
      final data = await get(
        '/activities/$activityId/track',
        token: token,
      );
      if (data is! Map<String, dynamic>) {
        throw ApiException(500, 'Resposta inesperada ao buscar rota');
      }
      return ActivityTrack.fromJson(data);
    } on ApiException catch (e) {
      if (e.statusCode == 404) return null;
      rethrow;
    }
  }

  // ---------- internos ----------

  Future<http.Response> _send(
    String method,
    String path, {
    String? token,
    Object? body,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final headers = <String, String>{
      'Accept': 'application/json',
      if (body != null) 'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };

    final encodedBody = body == null ? null : jsonEncode(body);

    late final http.Response response;
    switch (method) {
      case 'GET':
        response = await _client
            .get(uri, headers: headers)
            .timeout(const Duration(seconds: 30));
      case 'POST':
        response = await _client
            .post(uri, headers: headers, body: encodedBody)
            .timeout(const Duration(seconds: 30));
      case 'DELETE':
        response = await _client
            .delete(uri, headers: headers)
            .timeout(const Duration(seconds: 30));
      default:
        throw ArgumentError('Método HTTP não suportado: $method');
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(
        response.statusCode,
        _extractMessage(response.body) ?? 'Erro ${response.statusCode}',
      );
    }

    return response;
  }

  dynamic _decode(http.Response response) {
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