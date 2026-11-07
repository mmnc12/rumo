/**
 * Funções de API pra estatísticas agregadas (bloco 16).
 * Os endpoints são do usuário logado — não aceitam user_id.
 */

import { apiFetch } from "./client";
import type {
  StatsSummary,
  StatsWeeklyResponse,
  StatsMonthlyResponse,
} from "../types/api";

export interface StatsQuery {
  activity_type?: string;
}

/**
 * GET /activities/stats/summary — totais gerais do usuário logado.
 * `activity_type` opcional filtra (run/walk/cycle/...).
 */
export function getStatsSummary(
  params: StatsQuery = {}
): Promise<StatsSummary> {
  const qs = new URLSearchParams();
  if (params.activity_type) qs.set("activity_type", params.activity_type);
  const suffix = qs.toString() ? `?${qs}` : "";
  return apiFetch<StatsSummary>(`/activities/stats/summary${suffix}`);
}

/**
 * GET /activities/stats/weekly — resumo das últimas N semanas.
 * Retorna uma lista ordenada (o backend decide a ordem; conferir na UI).
 */
export function getStatsWeekly(
  weeks = 8,
  params: StatsQuery = {}
): Promise<StatsWeeklyResponse> {
  const qs = new URLSearchParams({ weeks: String(weeks) });
  if (params.activity_type) qs.set("activity_type", params.activity_type);
  return apiFetch<StatsWeeklyResponse>(`/activities/stats/weekly?${qs}`);
}

// [Sessão 13] Resumo mensal — espelho do weekly. Endpoint confirmado em
// produção: GET /activities/stats/monthly?months=N[&activity_type=...].
/**
 * GET /activities/stats/monthly — resumo dos últimos N meses.
 * Retorna uma lista ordenada (o backend decide a ordem; conferir na UI).
 */
export function getStatsMonthly(
  months = 6,
  params: StatsQuery = {}
): Promise<StatsMonthlyResponse> {
  const qs = new URLSearchParams({ months: String(months) });
  if (params.activity_type) qs.set("activity_type", params.activity_type);
  return apiFetch<StatsMonthlyResponse>(`/activities/stats/monthly?${qs}`);
}