import 'dart:convert';
import 'dart:io'; // [Sessão 31] File para upload multipart
import 'dart:typed_data'; // [Sessão 37] Uint8List para download binário

import 'package:http/http.dart' as http;

import '../models/activity.dart'; // [Sessão 31] Activity.fromJson no retorno do upload
import '../models/activity_track.dart';
import '../models/comment.dart';
import '../models/stats.dart'; // [Sessão 33] stats/summary + stats/by-type; [Sessão 38] weekly/monthly
import '../models/user.dart'; // [Sessão 34] User (UserPublic do backend)
import '../models/user_me.dart'; // [Sessão 39] UserMe (resposta de /auth/me e PUT /users/me)
import '../utils/download.dart'; // [Sessão 37] countZipEntries (EOCD fail-open)

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

  // [Sessão 51 — item 10.4 Onda B] Callback opcional disparado em 401
  // de chamadas AUTENTICADAS (não no login — 401 de senha errada é
  // esperado e não deve deslogar). O AuthService injeta este callback
  // após criar o ApiClient (setter público, mutável). O ApiClient NÃO
  // conhece AuthService nem navegação — só chama o callback. Quem
  // navega é o refreshListenable do GoRouter em main.dart.
  void Function()? onUnauthorized;

  /// Faz o login e retorna o token JWT.
  ///
  /// O backend espera `application/x-www-form-urlencoded` com
  /// `username` (e-mail) e `password`.
  ///
  /// [Sessão 51] NÃO dispara `onUnauthorized` — um 401 aqui é senha
  /// errada (usuário ainda não logado), não sessão expirada.
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

  // [Sessão 39] PUT autenticado — usado por updateMe (PUT /users/me).
  // Espelha o `post` (JSON body). Não existia porque até a S38 o app só
  // precisava de GET/POST/DELETE.
  Future<dynamic> put(
    String path, {
    Object? body,
    String? token,
  }) async {
    final response = await _send('PUT', path, token: token, body: body);
    return _decode(response);
  }

  /// DELETE autenticado.
  Future<dynamic> delete(String path, {String? token}) async {
    final response = await _send('DELETE', path, token: token);
    return _decode(response);
  }

  // ---------- Atividades (Sessão 32) ----------

  /// Lista atividades, opcionalmente filtradas por usuário.
  ///
  /// `GET /activities?user_id=&limit=&offset=`
  /// - `userId` null → todas (o backend filtra por visibilidade do viewer)
  /// - `userId` == currentUserId → "minhas atividades"
  /// - `userId` de terceiro → requer seguir (backend aplica; 403 se não seguir)
  ///
  /// Retorna `List<Activity>` puro — o backend NÃO devolve envelope de
  /// paginação (sem `total`/`has_more`). O cliente usa a regra
  /// "se voltou < limit, acabou".
  Future<List<Activity>> listActivities({
    String? userId,
    int limit = 20,
    int offset = 0,
    String? token,
  }) async {
    final qs = <String>[
      'limit=$limit',
      'offset=$offset',
      if (userId != null) 'user_id=$userId',
    ].join('&');
    final data = await get('/activities?$qs', token: token);
    if (data is! List) {
      throw ApiException(500, 'Resposta inesperada ao listar atividades');
    }
    return data
        .map((e) => Activity.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ---------- Busca de atividades (Sessão 36) ----------

  /// `GET /activities/search?q=&limit=` — busca atividades por texto
  /// em `title`/`description`.
  ///
  /// Auth: Bearer JWT. `q` mínimo 2 caracteres (o backend valida com
  /// `min_length=2`; o client também corta antes de disparar — paridade
  /// com `useActivitySearch` do web, que usa `enabled: trimmed.length >= 2`).
  ///
  /// Visibilidade (backend): dono OU seguido — mesma regra do feed. Se o
  /// viewer não segue o autor, a atividade dele não aparece.
  ///
  /// `limit` default 20 (mesmo do `useActivitySearch`). Rate limit do
  /// backend: 20/min por IP.
  ///
  /// Retorna `List<Activity>` (o `FeedItemResponse` do backend tem
  /// `author` E `user`; o `Activity.fromJson` lê `user` — fix da S36
  /// destravou o uso direto no mobile).
  ///
  /// [Sessão 36] `Uri.encodeQueryComponent` (não `Uri.encodeFull`) —
  /// paridade semântica com o `encodeURIComponent` do web.
  Future<List<Activity>> searchActivities({
    required String query,
    int limit = 20,
    String? token,
  }) async {
    final q = query.trim();
    if (q.length < 2) return const <Activity>[];
    final encoded = Uri.encodeQueryComponent(q);
    final data = await get(
      '/activities/search?q=$encoded&limit=$limit',
      token: token,
    );
    if (data is! List) {
      throw ApiException(500, 'Resposta inesperada em /activities/search');
    }
    return data
        .map((e) => Activity.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ---------- Stats (Sessão 33) ----------

  /// `GET /users/{userId}/stats/summary` — totais gerais.
  ///
  /// Auth: Bearer JWT. Visibilidade (backend): dono OU seguidor do dono
  /// (`_ensure_can_view_stats`). Nesta sessão o caller só usa o próprio
  /// userId (self-only) — o `_ensure_can_view_stats` deixa passar direto.
  ///
  /// Retorna `StatsSummary` (7 campos — total_activities, total_distance_m,
  /// total_duration_s, total_elevation_gain_m, total_calories,
  /// avg_pace_s_per_km?, avg_speed_mps?).
  Future<StatsSummary> getStatsSummary(
    String userId, {
    String? token,
  }) async {
    final data = await get('/users/$userId/stats/summary', token: token);
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada em stats/summary');
    }
    return StatsSummary.fromJson(data);
  }

  /// `GET /users/{userId}/stats/by-type?period=&compare=` — agregado por tipo.
  ///
  /// Auth: Bearer JWT. Mesma visibilidade do summary.
  ///
  /// `period`: "all" (todos os tempos; previous sempre null) |
  ///           "90d" (últimos 90 dias; default desta sessão) |
  ///           "1y" (últimos 365 dias).
  /// `compare`: "prev" (janela imediatamente anterior; default) |
  ///            "yoy" (mesmo período do ano anterior). Só tem efeito
  ///            quando period != "all".
  ///
  /// Retorna `StatsByTypeResponse { items }`, já ordenado pelo backend
  /// (total_activities DESC, tipo ASC no desempate).
  Future<StatsByTypeResponse> getStatsByType(
    String userId, {
    String period = '90d',
    String compare = 'prev',
    String? token,
  }) async {
    final data = await get(
      '/users/$userId/stats/by-type?period=$period&compare=$compare',
      token: token,
    );
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada em stats/by-type');
    }
    return StatsByTypeResponse.fromJson(data);
  }

  // [Sessão 38] Weekly + Monthly — paridade com web/src/hooks/useStats.ts
  // (defaults weeks=8, months=6). Shape confirmado em produção (P3a da S38):
  // { weeks|months: int, items: [ { period_start, total_activities,
  // total_distance_m, total_duration_s, total_calories } ] }.

  /// `GET /users/{userId}/stats/weekly?weeks=N` — resumo semanal.
  ///
  /// Auth: Bearer JWT. Visibilidade: dono OU seguidor do dono (mesma
  /// regra do summary). `weeks` default 8 (paridade com `useStatsWeekly`
  /// do web). Retorna `StatsWeeklyResponse { weeks, items }` com items
  /// em ordem crescente de `period_start` (o caller NÃO reordena).
  Future<StatsWeeklyResponse> getStatsWeekly(
    String userId, {
    int weeks = 8,
    String? token,
  }) async {
    final data = await get(
      '/users/$userId/stats/weekly?weeks=$weeks',
      token: token,
    );
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada em stats/weekly');
    }
    return StatsWeeklyResponse.fromJson(data);
  }

  /// `GET /users/{userId}/stats/monthly?months=N` — resumo mensal.
  ///
  /// Auth: Bearer JWT. Visibilidade: dono OU seguidor do dono. `months`
  /// default 6 (paridade com `useStatsMonthly` do web). Retorna
  /// `StatsMonthlyResponse { months, items }` — mesma semântica do weekly
  /// (só muda a janela de agregação).
  Future<StatsMonthlyResponse> getStatsMonthly(
    String userId, {
    int months = 6,
    String? token,
  }) async {
    final data = await get(
      '/users/$userId/stats/monthly?months=$months',
      token: token,
    );
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada em stats/monthly');
    }
    return StatsMonthlyResponse.fromJson(data);
  }

  // ---------- Perfil público e follows (Sessão 34) ----------

  /// `GET /users/{userId}` — perfil público de qualquer usuário.
  ///
  /// Auth: Bearer JWT. Retorna `User` (4 campos: id, username, full_name,
  /// is_active). NÃO tem email (use /auth/me pro self) e NÃO tem avatar_url
  /// (o backend não devolve). 404 quando o id não existe.
  Future<User> getUser(String userId, {String? token}) async {
    final data = await get('/users/$userId', token: token);
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada em /users/{id}');
    }
    return User.fromJson(data);
  }

  // [Sessão 39] PUT /users/me — atualiza o próprio perfil.
  //
  // Semântica de "não mandou" vs "mandou null" (backend usa
  // model_dump(exclude_unset=True)):
  // - campo AUSENTE do map  → não toca no banco
  // - campo = null          → limpa o campo
  // - campo com valor       → atualiza
  //
  // O caller (EditProfilePage) monta o Map só com os campos que o usuário
  // tocou. Campo intocado não entra no map (ausente). Campo que o usuário
  // tocou em "Limpar" entra como `null` explícito. Campo que o usuário
  // editou entra com o valor numérico/string.
  //
  // Retorna `UserMe` (mesmo shape do /auth/me) já com o estado pós-update,
  // pra UI refletir sem GET extra (S39 — paridade com o backend que
  // devolve UserResponse).
  //
  // Erros: 401 (sem token), 422 (validação Pydantic: range de weight/height,
  // max_length de full_name, campo proibido como email/username).
  Future<UserMe> updateMe({
    String? fullName,
    double? weightKg,
    double? heightCm,
    required Map<String, bool> fieldsToClear,
    String? token,
  }) async {
    final body = <String, dynamic>{};
    if (fullName != null) body['full_name'] = fullName;
    if (weightKg != null) body['weight_kg'] = weightKg;
    if (heightCm != null) body['height_cm'] = heightCm;
    fieldsToClear.forEach((key, shouldClear) {
      if (shouldClear) body[key] = null;
    });

    final data = await put('/users/me', body: body, token: token);
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada em PUT /users/me');
    }
    return UserMe.fromJson(data);
  }

  /// `POST /users/{userId}/follow` — segue um usuário.
  ///
  /// 204 sem body. O backend valida que não é self (400 se tentar seguir
  /// a si mesmo) e que o target existe (404). O caller não precisa se
  /// preocupar com o corpo — `delete`/`post` já aceitam 204.
  Future<void> followUser(String userId, {String? token}) async {
    await post('/users/$userId/follow', token: token);
  }

  /// `DELETE /users/{userId}/follow` — deixa de seguir.
  ///
  /// 204 sem body. Idempotente no backend (não falha se já não seguia).
  Future<void> unfollowUser(String userId, {String? token}) async {
    await delete('/users/$userId/follow', token: token);
  }

  /// `GET /users/{userId}/following?limit=&offset=` — quem o usuário segue.
  ///
  /// Retorna `List<User>`. Paginação explícita (limit/offset). Default
  /// limit=100 cobre o caso de uso do `isFollowing` (inferência por lista);
  /// se um dia precisar paginar de verdade, aumentar ou iterar.
  Future<List<User>> listFollowing({
    required String userId,
    int limit = 100,
    int offset = 0,
    String? token,
  }) async {
    final qs = 'limit=$limit&offset=$offset';
    final data = await get('/users/$userId/following?$qs', token: token);
    if (data is! List) {
      throw ApiException(500, 'Resposta inesperada em /users/{id}/following');
    }
    return data
        .map((e) => User.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// `isFollowing` — infere se `meId` segue `targetUserId`.
  ///
  /// O backend NÃO tem `GET /users/{id}/is-following` (mesma limitação
  /// que o web contorna em `useProfile.ts` → `useIsFollowing`). A
  /// inferência é: buscar `/users/{meId}/following` e checar se o alvo
  /// está na lista. Custa 1 request extra por perfil aberto.
  ///
  /// Self → `false` (o backend não deixa seguir a si mesmo; a UI trata
  /// `isSelf` separado via `meId == targetUserId`).
  Future<bool> isFollowing({
    required String meId,
    required String targetUserId,
    String? token,
  }) async {
    if (meId == targetUserId) return false;
    final following = await listFollowing(
      userId: meId,
      limit: 100,
      token: token,
    );
    return following.any((u) => u.id == targetUserId);
  }

  // ---------- Busca de usuários (Sessão 35) ----------

  /// `GET /users/search?q=&limit=` — busca usuários por username/full_name.
  ///
  /// Auth: Bearer JWT. `q` mínimo 2 caracteres (o backend valida; o client
  /// também corta antes de disparar — paridade com o `useUserSearch` do web,
  /// que usa `enabled: trimmed.length >= 2`). `limit` default 20 (mesmo do
  /// `useUserSearch` do web). Rate limit do backend: 20/min por IP.
  ///
  /// Retorna `List<User>` (mesmos 4 campos do `/users/{id}`). Vazio =
  /// nenhum match (não é erro). 429 = rate limit (vira `ApiException` com
  /// a mensagem do backend).
  ///
  /// [Sessão 35] `Uri.encodeQueryComponent` (não `Uri.encodeFull`) — paridade
  /// semântica com o `encodeURIComponent` do web. Aceita espaços, acentos,
  /// e o que mais o usuário digitar.
  Future<List<User>> searchUsers({
    required String query,
    int limit = 20,
    String? token,
  }) async {
    final q = query.trim();
    if (q.length < 2) return const <User>[];
    final encoded = Uri.encodeQueryComponent(q);
    final data = await get('/users/search?q=$encoded&limit=$limit', token: token);
    if (data is! List) {
      throw ApiException(500, 'Resposta inesperada em /users/search');
    }
    return data
        .map((e) => User.fromJson(e as Map<String, dynamic>))
        .toList();
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
  ///
  /// [Sessão 51] Dispara `onUnauthorized` em 401 — upload autenticado.
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
      // [Sessão 51] 401 em upload autenticado → dispara callback.
      if (response.statusCode == 401) onUnauthorized?.call();
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

  // ---------- Export (Sessão 37) ----------

  /// `GET /activities/{id}/export?format=csv|gpx` — baixa bytes do export unitário.
  ///
  /// Auth: Bearer JWT. Permissão (backend): dono OU seguidor do dono
  /// (404 caso contrário, mesma regra do detalhe). `format=csv` funciona
  /// com/sem rota; `format=gpx` exige rota (404 "Atividade não possui rota").
  ///
  /// Retorna `({bytes, filename, contentType})`:
  /// - `bytes`: corpo binário cru (Uint8List).
  /// - `filename`: parseado do `Content-Disposition` (`rumo_<id>_<type>.<ext>`);
  ///   se faltar, cai em `rumo_<id>.<format>`.
  /// - `contentType`: `text/csv` ou `application/gpx+xml` (com `; charset=utf-8`).
  ///
  /// O caller (ActivityDetailPage) decide onde salvar/compartilhar via
  /// `saveAndShare` (utils/download.dart).
  Future<({Uint8List bytes, String filename, String contentType})>
      downloadActivityExport({
    required String activityId,
    required String format,
    String? token,
  }) async {
    assert(format == 'csv' || format == 'gpx', 'format inválido: $format');
    return _fetchBlob(
      '/activities/$activityId/export?format=$format',
      fallbackFilename: 'rumo_$activityId.$format',
      token: token,
    );
  }

  /// `GET /activities/export?format=&from=&to=` — baixa bytes do export em lote (ZIP).
  ///
  /// Auth: Bearer JWT. **Self-only** (diferente do unitário — o backend
  /// só exporta as atividades do viewer autenticado). Saída: ZIP com
  /// 1 arquivo por atividade.
  ///
  /// - `format=csv` (default): todas as atividades do filtro (com/sem rota).
  /// - `format=gpx`: só com rota (backend omite as sem).
  /// - `from`/`to` (YYYY-MM-DD, UTC, inclusivo). Omitir = sem limite.
  /// - 0 atividades → ZIP vazio (200, não é erro).
  /// - `from > to` → 422. `format` inválido → 422.
  ///
  /// Retorna o mesmo shape do unitário + `entryCount`:
  /// - `entryCount`: número de arquivos no ZIP, lido via `countZipEntries`
  ///   (EOCD, fail-open). `-1` quando o ZIP não pôde ser lido (o caller
  ///   decide como usar — o download já aconteceu).
  Future<
      ({
        Uint8List bytes,
        String filename,
        String contentType,
        int entryCount,
      })> downloadActivityExportBulk({
    required String format,
    String? from,
    String? to,
    String? token,
  }) async {
    assert(format == 'csv' || format == 'gpx', 'format inválido: $format');
    final qs = <String>[
      'format=$format',
      if (from != null && from.isNotEmpty) 'from=$from',
      if (to != null && to.isNotEmpty) 'to=$to',
    ].join('&');

    final blob = await _fetchBlob(
      '/activities/export?$qs',
      fallbackFilename: 'rumo_export.zip',
      token: token,
    );

    final entryCount = countZipEntries(blob.bytes);
    return (
      bytes: blob.bytes,
      filename: blob.filename,
      contentType: blob.contentType,
      entryCount: entryCount,
    );
  }
    // ---------- Followers (Sessão 37) ----------

  /// `GET /users/{userId}/followers?limit=&offset=` — quem segue o usuário.
  ///
  /// Espelho de `listFollowing`. Auth: Bearer JWT. Retorna `List<User>`.
  /// Paginação explícita (limit/offset). Default limit=100 cobre o caso
  /// de uso da tela de perfil (abas Seguidores/Seguindo).
  Future<List<User>> listFollowers({
    required String userId,
    int limit = 100,
    int offset = 0,
    String? token,
  }) async {
    final qs = 'limit=$limit&offset=$offset';
    final data = await get('/users/$userId/followers?$qs', token: token);
    if (data is! List) {
      throw ApiException(500, 'Resposta inesperada em /users/{id}/followers');
    }
    return data
        .map((e) => User.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ---------- Cadastro (Sessão 49) ----------

  /// `POST /auth/register` — cria um novo usuário.
  ///
  /// Endpoint PÚBLICO (não requer token). O backend valida:
  /// - `email` único (EmailStr)
  /// - `username` único, min 3 max 50, pattern `^[a-zA-Z0-9_]+$`
  /// - `password` min 8 max 128
  /// - `full_name` opcional, max 120
  /// - `weight_kg` opcional, 0 < x < 500
  /// - `height_cm` opcional, 0 < x < 300
  /// - `birth_date` opcional (date ISO)
  ///
  /// Sucesso: 201 com `UserResponse` (mesmo shape do /auth/me → `UserMe`).
  /// Erro:
  /// - 409 com `detail` = "Email já cadastrado" OU "Username já cadastrado"
  ///   (o caller deve preservar `e.message` no 409 — S48d)
  /// - 422 validação Pydantic
  /// - 429 rate limit (3 cadastros/hora por IP)
  Future<UserMe> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
    double? weightKg,
    double? heightCm,
    String? birthDate, // YYYY-MM-DD
  }) async {
    final body = <String, dynamic>{
      'email': email,
      'username': username,
      'password': password,
      'full_name': ?(fullName != null && fullName.trim().isNotEmpty)
          ? fullName.trim()
          : null,
      'weight_kg': ?weightKg,
      'height_cm': ?heightCm,
      'birth_date': ?(birthDate != null && birthDate.isNotEmpty)
          ? birthDate
          : null,
    };

    final data = await post('/auth/register', body: body);
    if (data is! Map<String, dynamic>) {
      throw ApiException(500, 'Resposta inesperada em /auth/register');
    }
    return UserMe.fromJson(data);
  }

  // ---------- internos ----------

  /// GET binário autenticado (Sessão 37).
  ///
  /// Diferenças do `_send`:
  /// - `Accept: */*` (não força `application/json`).
  /// - Retorna `bodyBytes` cru (não `jsonDecode`).
  /// - Lê `Content-Type` e `Content-Disposition` da resposta.
  ///
  /// O `_extractMessage` continua funcionando pra erros: o FastAPI devolve
  /// JSON (`{"detail": "..."}`) mesmo no export (o erro é JSON, o sucesso
  /// é o blob). Quando o corpo do erro não é JSON, cai no fallback
  /// `Erro <status>`.
  ///
  /// [Sessão 51] Dispara `onUnauthorized` em 401 — export autenticado.
  Future<({Uint8List bytes, String filename, String contentType})> _fetchBlob(
    String path, {
    required String fallbackFilename,
    String? token,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final headers = <String, String>{
      'Accept': '*/*',
      if (token != null) 'Authorization': 'Bearer $token',
    };

    late final http.Response response;
    try {
      response = await _client
          .get(uri, headers: headers)
          .timeout(const Duration(seconds: 60));
    } catch (e) {
      throw ApiException(0, 'Falha de rede no export: $e');
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      // [Sessão 51] 401 em export autenticado → dispara callback.
      if (response.statusCode == 401) onUnauthorized?.call();
      throw ApiException(
        response.statusCode,
        _extractMessage(response.body) ?? 'Erro ${response.statusCode}',
      );
    }

    final contentType =
        response.headers['content-type'] ?? 'application/octet-stream';
    final filename = _parseContentDisposition(
      response.headers['content-disposition'],
      fallback: fallbackFilename,
    );

    return (
      bytes: Uint8List.fromList(response.bodyBytes),
      filename: filename,
      contentType: contentType,
    );
  }

  /// Extrai `filename="..."` do header `Content-Disposition`.
  ///
  /// Formato esperado (S21/S22 do backend):
  /// `attachment; filename="rumo_<id>_<type>.csv"` ou
  /// `attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"`.
  ///
  /// Se o header faltar ou não tiver `filename="..."`, devolve [fallback].
  String _parseContentDisposition(
    String? header, {
    required String fallback,
  }) {
    if (header == null || header.isEmpty) return fallback;
    final match = RegExp(r'filename="([^"]+)"').firstMatch(header);
    if (match == null) return fallback;
    final name = match.group(1);
    if (name == null || name.isEmpty) return fallback;
    return name;
  }

  /// [Sessão 51] Dispara `onUnauthorized` em 401 — chamadas autenticadas
  /// (GET/POST/PUT/DELETE). O `login` NÃO usa `_send` (é multipart
  /// urlencoded próprio) e por isso não dispara — 401 de senha errada
  /// é esperado e não deve deslogar.
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
      // [Sessão 39] PUT — necessário pro updateMe (PUT /users/me).
      case 'PUT':
        response = await _client
            .put(uri, headers: headers, body: encodedBody)
            .timeout(const Duration(seconds: 30));
      case 'DELETE':
        response = await _client
            .delete(uri, headers: headers)
            .timeout(const Duration(seconds: 30));
      default:
        throw ArgumentError('Método HTTP não suportado: $method');
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      // [Sessão 51] 401 em chamada autenticada → dispara callback.
      if (response.statusCode == 401) onUnauthorized?.call();
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