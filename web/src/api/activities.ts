/**
 * Funções de API pra atividades.
 * (Upload GPX entra aqui no 13a.3 — por enquanto só lista e detalhe.)
 */

import { apiFetch } from "./client";
import type { Activity } from "../types/api";
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
 * GET /activities/{id} — detalhe de uma atividade.
 * (Vai ser usado no 13a.4, mas já deixo aqui pra não criar arquivo novo.)
 */
export async function getActivity(id: string): Promise<Activity> {
  return apiFetch<Activity>(`/activities/${id}`);
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