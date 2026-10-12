/**
 * Funções de API pra atividades.
 * (Upload GPX entra aqui no 13a.3 — por enquanto só lista e detalhe.)
 */

import { apiFetch } from "./client";
import type { Activity } from "../types/api";

export interface ListActivitiesParams {
  limit?: number;
  offset?: number;
}

/**
 * GET /activities?limit=&offset= — lista atividades do usuário logado.
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