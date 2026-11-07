/**
 * Funções de API pra estatísticas agregadas (bloco 16).
 * Os endpoints são do usuário logado — não aceitam user_id.
 */

import { apiFetch } from "./client";
import type {
  StatsSummary,
  StatsWeeklyResponse,
  StatsMonthlyResponse,
  StatsByTypeResponse,
} from "../types/api";

export interface StatsQuery {
  activity_type?: string;
}

// [Sessão 17] Janela temporal do drill-down por tipo.
// Espelha o enum aceito pelo backend em GET /activities/stats/by-type.
export type StatsPeriod = "all" | "90d" | "1y";

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

// [Sessão 13] Resumo mensal — espelho do weekly.
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

// [Sessão 14 — B1] Drill-down por tipo de atividade.
// [Sessão 17] Adicionado `period` (all|90d|1y) — janela temporal opcional.
// [Sessão 18] Cada item agora pode trazer `previous` (janela anterior).
/**
 * GET /activities/stats/by-type — agregado por tipo de atividade.
 * O backend já ordena por total_activities DESC (desempate por tipo ASC).
 *
 * `period` filtra por `started_at`:
 *  - `all` (default): todos os tempos.
 *  - `90d`: últimos 90 dias.
 *  - `1y`: últimos 365 dias.
 *
 * [Sessão 18] Para `90d`/`1y`, cada item traz `previous` com as 5
 * métricas da janela *imediatamente anterior* (90d→[now-180d, now-90d);
 * 1y→[now-730d, now-365d)). `previous` é `null` para `period="all"` ou
 * quando o tipo não teve atividade na janela anterior. O shape está
 * em `StatsByTypeItem` (types/api.ts).
 *
 * Sempre manda o param na URL (inclusive `all`), para o log do backend
 * refletir a intenção e não depender do default do server no futuro.
 */
export function getStatsByType(
  period: StatsPeriod = "all"
): Promise<StatsByTypeResponse> {
  const qs = new URLSearchParams({ period });
  return apiFetch<StatsByTypeResponse>(`/activities/stats/by-type?${qs}`);
}