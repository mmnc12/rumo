/**
 * Funções de API pra atividades.
 * (Upload GPX entra aqui no 13a.3 — por enquanto só lista e detalhe.)
 */

import { apiFetch, apiFetchBlob } from "./client";
import type { Activity, ActivityDetail } from "../types/api";
import type { TrackResponse } from "../types/api";

export interface ListActivitiesParams {
  limit?: number;
  offset?: number;
  /** Filtra atividades de outro usuário (requer seguir o dono). */
  userId?: string;
}

/**
 * GET /activities?limit=&offset=&user_id= — lista atividades.
 * - Sem `userId`: próprias atividades.
 * - Com `userId`: do usuário alvo (o backend exige follow; 403 caso contrário).
 * O backend já ordena por started_at desc.
 */
export async function listActivities(
  params: ListActivitiesParams = {}
): Promise<Activity[]> {
  const limit = params.limit ?? 20;
  const offset = params.offset ?? 0;
  const qs = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  if (params.userId) qs.set("user_id", params.userId);
  return apiFetch<Activity[]>(`/activities?${qs.toString()}`);
}

/**
 * GET /activities/{id} — detalhe de uma atividade (com autor aninhado).
 *
 * O backend retorna ActivityDetail (Activity + author). Não precisa
 * de um segundo request pra buscar o perfil do dono.
 */
export async function getActivity(id: string): Promise<ActivityDetail> {
  return apiFetch<ActivityDetail>(`/activities/${id}`);
}

/**
 * DELETE /activities/{id} — remove uma atividade do usuário.
 * 204 No Content.
 */
export async function deleteActivity(id: string): Promise<void> {
  return apiFetch<void>(`/activities/${id}`, { method: "DELETE" });
}

// ===== Upload GPX =====

export interface UploadGpxMeta {
  title?: string;
  activity_type?: string;
  description?: string;
}

/**
 * POST /activities/upload — envia um arquivo .gpx (multipart).
 *
 * O backend parseia o GPX, calcula distância/pace/elevação e devolve
 * o ActivityResponse completo. `rawBody` passa o FormData cru pro fetch,
 * deixando o browser setar o Content-Type com boundary.
 */
export async function uploadGpx(
  file: File,
  meta: UploadGpxMeta = {}
): Promise<Activity> {
  const form = new FormData();
  form.append("file", file);
  if (meta.title) form.append("title", meta.title);
  if (meta.activity_type) form.append("activity_type", meta.activity_type);
  if (meta.description) form.append("description", meta.description);

  return apiFetch<Activity>("/activities/upload", {
    method: "POST",
    rawBody: form,
  });
}

/**
 * Busca a geometria da rota de uma atividade (GeoJSON-like).
 *
 * Endpoint dedicado — não vem no ActivityResponse pra não pesar a listagem.
 * Só o dono da atividade acessa (404 caso contrário).
 */
export function getActivityTrack(id: string): Promise<TrackResponse> {
  return apiFetch<TrackResponse>(`/activities/${id}/track`);
}

// ===== Export CSV/GPX — [Sessão 21] =====

export type ActivityExportFormat = "csv" | "gpx";

/**
 * Dispara o download de um blob como arquivo, sem vazar memória.
 *
 * Cria uma URL temporária pro Blob, ancora num `<a download>`, clica e
 * revoga. `setTimeout(0)` no `revokeObjectURL` porque o Chrome pode
 * começar o download de forma assíncrona — revogar imediatamente cancela.
 */
function _triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  // `style.display = "none"` evita flash do link no DOM em alguns browsers.
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

/**
 * GET /activities/{id}/export?format=csv|gpx — baixa a atividade.
 *
 * CSV: metadados (1 linha). GPX: geometria completa (exige rota no
 * backend — 404 "Atividade não possui rota").
 *
 * Auth: mesma regra do detalhe (dono ou seguidor; senão 404). Erros
 * sobem como `ApiError` (o chamador trata 404 mostrando aviso, por ex.).
 *
 * Filename: vem do `Content-Disposition` do backend
 * (`rumo_<id>_<type>.<ext>`); se faltar, cai em `rumo_<id>.<format>`.
 */
export async function downloadActivityExport(
  id: string,
  format: ActivityExportFormat
): Promise<void> {
  const { blob, filename } = await apiFetchBlob(
    `/activities/${id}/export?format=${format}`
  );
  _triggerDownload(blob, filename ?? `rumo_${id}.${format}`);
}

// ===== Export em lote — [Sessão 23] =====
//
// Paridade de UI com o endpoint GET /activities/export (backend S22).
// Auth: self-only (diferente do unitário — o backend só exporta as
// atividades do viewer autenticado). Retorna um ZIP com N arquivos.

export interface DownloadActivityExportBulkParams {
  format: ActivityExportFormat;
  /** Data inicial inclusiva (YYYY-MM-DD, UTC). Omitir = sem limite. */
  from?: string;
  /** Data final inclusiva (YYYY-MM-DD, UTC). Omitir = sem limite. */
  to?: string;
}

// [Sessão 29] Resultado do export em lote. `entryCount` é o número de
// arquivos dentro do ZIP — o caller (ProfilePage) usa pra decidir a
// mensagem de feedback ("Download iniciado (N atividades)." vs.
// "Nenhuma atividade no período — ZIP vazio.").
// `-1` significa "não foi possível ler o ZIP" (fail-open: o download
// já aconteceu, o feedback cai no texto genérico de sucesso).
export interface DownloadActivityExportBulkResult {
  entryCount: number;
}

/**
 * [Sessão 29] Conta entradas de um ZIP lendo o End Of Central Directory.
 *
 * Por que EOCD e não descer no central directory:
 * - O ZIP do backend (FastAPI `zipfile.ZipFile`) sempre tem EOCD.
 * - O campo `totalEntries` (offset 10, uint16 LE) já é o número de
 *   arquivos — pro `format=csv` são todas as atividades; pro
 *   `format=gpx` o backend já filtra as sem rota, então o número
 *   também casa com "atividades com rota".
 * - Não exige ZIP64 (arquivos pequenos: ZIP do Rumo fica na casa dos
 *   KBs mesmo com 100+ atividades).
 * - Sem dependência externa (nada de `jszip`).
 *
 * Retorna `-1` em qualquer falha (ZIP malformado, ZIP64, buffer
 * truncado) — o chamador decide o que fazer. NÃO lança.
 */
function _countZipEntries(arrayBuffer: ArrayBuffer): number {
  // ZIP64 tem EOCD64 antes do EOCD normal; nesse caso o uint16 do
  // EOCD pode estar com 0xFFFF como sentinela. Tratamos como
  // "não consegui contar" (fail-open) — não vale o custo pra ZIP
  // de export de atividades (sempre < 4 GB / < 65535 arquivos).
  if (arrayBuffer.byteLength < 22) return -1;

  const view = new DataView(arrayBuffer);
  const len = arrayBuffer.byteLength;

  // EOCD pode ter comentário variável (até 65535 bytes). O padrão
  // é varrer do fim pra trás nessa janela procurando a assinatura.
  const EOCD_SIG = 0x06054b50;
  const maxComment = 0xffff;
  const searchStart = Math.max(0, len - 22 - maxComment);

  let eocdOffset = -1;
  // Varre de trás pra frente: o EOCD real é o primeiro (mais próximo
  // do fim) que tem a assinatura e cujo comprimento bate com o resto.
  for (let i = len - 22; i >= searchStart; i--) {
    if (view.getUint32(i, true) === EOCD_SIG) {
      eocdOffset = i;
      break;
    }
  }

  if (eocdOffset === -1) return -1;

  // Layout do EOCD (little-endian):
  //   offset  0  uint32  signature 0x06054b50
  //   offset  4  uint16  número do disco
  //   offset  6  uint16  disco do central directory
  //   offset  8  uint16  entradas neste disco
  //   offset 10  uint16  total de entradas
  //   offset 12  uint32  tamanho do central directory
  //   offset 16  uint32  offset do central directory
  //   offset 20  uint16  tamanho do comentário
  const totalEntries = view.getUint16(eocdOffset + 10, true);

  // 0xFFFF como sentinela indica ZIP64 — não suportamos (fail-open).
  if (totalEntries === 0xffff) return -1;

  return totalEntries;
}

/**
 * GET /activities/export?format=&from=&to= — baixa TODAS as suas
 * atividades (do filtro) como um ZIP, com 1 arquivo por atividade.
 *
 * - `format=csv`: todas as atividades do filtro (com ou sem rota).
 * - `format=gpx`: só as com rota (backend omite as sem — não gera GPX vazio).
 * - Filtro opcional `from`/`to` (YYYY-MM-DD, inclusivo nas duas pontas).
 * - 0 atividades no filtro → ZIP vazio (200, não é erro).
 * - `from > to` → 422. `format` inválido → 422.
 *
 * O nome do arquivo (`rumo_export_<YYYYMMDD-HHMMSS>.zip`) vem do header
 * `Content-Disposition`; se faltar, cai em `rumo_export.zip`.
 *
 * [Sessão 29] Passa a devolver `{ entryCount }` — o número de arquivos
 * dentro do ZIP, contado localmente via EOCD. `-1` quando o ZIP não
 * pôde ser lido (fail-open: o download já aconteceu, o caller decide
 * como usar). O download em si continua acontecendo dentro desta
 * função (via `_triggerDownload`), igual antes.
 */
export async function downloadActivityExportBulk(
  params: DownloadActivityExportBulkParams
): Promise<DownloadActivityExportBulkResult> {
  const qs = new URLSearchParams();
  qs.set("format", params.format);
  if (params.from) qs.set("from", params.from);
  if (params.to) qs.set("to", params.to);

  const { blob, filename } = await apiFetchBlob(
    `/activities/export?${qs.toString()}`
  );

  // [Sessão 29] Lê o ZIP ANTES de disparar o download, pra podermos
  // devolver a contagem. `blob.arrayBuffer()` é barato (ZIP pequeno)
  // e não consome o blob — `_triggerDownload` continua funcionando.
  let entryCount: number;
  try {
    entryCount = _countZipEntries(await blob.arrayBuffer());
  } catch {
    // Fail-open: qualquer erro na leitura do ZIP não pode derrubar o
    // export — o usuário ainda tem o arquivo na mão.
    entryCount = -1;
  }

  _triggerDownload(blob, filename ?? "rumo_export.zip");

  return { entryCount };
}