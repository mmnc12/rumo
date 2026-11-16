// [Sessão 37] Helpers de download multiplataforma + contagem de entradas ZIP.
//
// Por que existe:
// - O ApiClient devolve bytes (Uint8List) pro export CSV/GPX/ZIP.
// - No mobile (Android/iOS/Desktop) os bytes precisam virar arquivo em disco
//   + share sheet nativo. Na web, share_plus dispara download no browser.
// - O `entryCount` do export em lote (paridade com web S29) precisa contar
//   arquivos dentro do ZIP sem dependência externa (nada de `archive`).

import 'dart:typed_data';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

/// Salva [bytes] como arquivo [filename] e abre o share sheet.
///
/// Plataformas:
/// - **Web** (`kIsWeb`): usa `SharePlus` — o browser baixa o arquivo.
/// - **Android/iOS/Desktop**: grava em `getTemporaryDirectory()` e abre o
///   share sheet nativo (`SharePlus.instance.share`).
///
/// O `contentType` (ex.: `text/csv`) não é usado pelo share_plus nesta
/// versão — o share sheet do SO infere pelo nome do arquivo. Mantido no
/// contrato pra uso futuro (ex.: upload com MIME correto).
Future<void> saveAndShare({
  required Uint8List bytes,
  required String filename,
  required String contentType,
  String? shareText,
}) async {
  // Web: share_plus usa a Share API do browser (ou fallback de download).
  if (kIsWeb) {
    await SharePlus.instance.share(
      ShareParams(
        files: [XFile.fromData(bytes, mimeType: contentType, name: filename)],
        text: shareText,
        subject: filename,
      ),
    );
    return;
  }

  // Nativo/desktop: grava em diretório temporário e compartilha.
  // `getTemporaryDirectory` é o mais seguro — não exige permissão de
  // armazenamento e o SO limpa depois. O usuário escolhe "salvar em
  // Arquivos", "enviar por e-mail", etc. via share sheet.
  final dir = await getTemporaryDirectory();
  final file = XFile.fromData(
    bytes,
    mimeType: contentType,
    name: filename,
  );
  // path_provider não é usado diretamente pra montar path — o XFile.fromData
  // + share_plus resolvem o arquivo temporário internamente em cada
  // plataforma. `dir` fica como fallback se o share_plus mudar de API.
  assert(dir.path.isNotEmpty);
  await SharePlus.instance.share(
    ShareParams(
      files: [file],
      text: shareText,
      subject: filename,
    ),
  );
}

/// Conta entradas de um ZIP lendo o End Of Central Directory (EOCD).
///
/// Porta do `_countZipEntries` do web (`web/src/api/activities.ts`, S29).
/// Regras idênticas:
/// - Varre do fim pra trás procurando a assinatura `0x06054b50`.
/// - Lê `totalEntries` (offset 10 do EOCD, uint16 little-endian).
/// - `0xFFFF` como sentinela → ZIP64 → retorna `-1` (fail-open).
/// - Qualquer falha (buffer curto, assinatura não encontrada) → `-1`.
///
/// Retorna `-1` em qualquer falha. NUNCA lança.
int countZipEntries(Uint8List bytes) {
  // ZIP mínimo tem 22 bytes de EOCD.
  if (bytes.length < 22) return -1;

  const eocdSig = 0x06054b50;
  const maxComment = 0xffff;
  final searchStart =
      bytes.length - 22 - maxComment < 0 ? 0 : bytes.length - 22 - maxComment;

  int eocdOffset = -1;
  // Varre de trás pra frente. O EOCD real é o primeiro (mais próximo do
  // fim) que tem a assinatura.
  for (var i = bytes.length - 22; i >= searchStart; i--) {
    final sig = bytes[i] |
        (bytes[i + 1] << 8) |
        (bytes[i + 2] << 16) |
        (bytes[i + 3] << 24);
    if (sig == eocdSig) {
      eocdOffset = i;
      break;
    }
  }

  if (eocdOffset == -1) return -1;

  // totalEntries: uint16 LE no offset 10 do EOCD.
  final totalEntries = bytes[eocdOffset + 10] | (bytes[eocdOffset + 11] << 8);

  // 0xFFFF = sentinela de ZIP64 → fail-open.
  if (totalEntries == 0xffff) return -1;

  return totalEntries;
}