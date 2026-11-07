import { useQuery } from "@tanstack/react-query";

import {
  getStatsSummary,
  getStatsWeekly,
  getStatsMonthly,
  getStatsByType,
  type StatsPeriod,
} from "../api/stats";
import type {
  StatsSummary,
  StatsWeeklyResponse,
  StatsMonthlyResponse,
  StatsByTypeResponse,
} from "../types/api";

// ===== Query keys =====

export const statsKeys = {
  all: ["stats"] as const,
  summary: (activityType?: string) =>
    [...statsKeys.all, "summary", activityType ?? "all"] as const,
  weekly: (weeks: number, activityType?: string) =>
    [...statsKeys.all, "weekly", weeks, activityType ?? "all"] as const,
  // [Sessão 13] Chave para o mensal — mesmo padrão do weekly.
  monthly: (months: number, activityType?: string) =>
    [...statsKeys.all, "monthly", months, activityType ?? "all"] as const,
  // [Sessão 14 — B1] Drill-down por tipo.
  // [Sessão 17] Chave inclui `period` para o React Query refazer a chamada
  // quando o usuário troca o filtro de janela temporal.
  // [Sessão 18] O payload já traz `previous` por item (mesma chamada, sem
  // novo hook nem nova key — a janela anterior é derivada no backend).
  byType: (period: StatsPeriod) =>
    [...statsKeys.all, "by-type", period] as const,
};

// ===== Summary =====

/**
 * Totais gerais do usuário logado.
 *
 * `enabled` controla se dispara (só no próprio perfil).
 * staleTime 60s: stats agregadas mudam pouco (só com novo upload/delete).
 */
export function useStatsSummary(
  activityType?: string,
  enabled = true
) {
  return useQuery<StatsSummary>({
    queryKey: statsKeys.summary(activityType),
    queryFn: () => getStatsSummary({ activity_type: activityType }),
    enabled,
    staleTime: 60_000,
    retry: 1,
  });
}

// ===== Weekly =====

/**
 * Resumo semanal das últimas N semanas.
 *
 * `enabled` controla se dispara (só no próprio perfil).
 * staleTime 60s: idem summary.
 */
export function useStatsWeekly(
  weeks = 8,
  activityType?: string,
  enabled = true
) {
  return useQuery<StatsWeeklyResponse>({
    queryKey: statsKeys.weekly(weeks, activityType),
    queryFn: () => getStatsWeekly(weeks, { activity_type: activityType }),
    enabled,
    staleTime: 60_000,
    retry: 1,
  });
}

// ===== Monthly =====

// [Sessão 13] Hook mensal — espelho do useStatsWeekly.
/**
 * Resumo mensal dos últimos N meses.
 *
 * `enabled` controla se dispara (só no próprio perfil).
 * staleTime 60s: idem summary/weekly.
 */
export function useStatsMonthly(
  months = 6,
  activityType?: string,
  enabled = true
) {
  return useQuery<StatsMonthlyResponse>({
    queryKey: statsKeys.monthly(months, activityType),
    queryFn: () => getStatsMonthly(months, { activity_type: activityType }),
    enabled,
    staleTime: 60_000,
    retry: 1,
  });
}

// ===== By type [Sessão 14 — B1] =====

// [Sessão 17] Adicionado `period` como primeiro arg (default "all").
// A query key inclui `period` — trocar de janela dispara refetch automaticamente.
// [Sessão 18] Cada item do payload agora pode trazer `previous` (janela
// imediatamente anterior). Nada muda no hook: o dado vem no mesmo response.
/**
 * Agregado por tipo de atividade do usuário logado.
 *
 * Sem filtro de tipo (o objetivo é justamente ver TODOS os tipos).
 * `period` filtra por janela temporal: `all` (default), `90d`, `1y`.
 * Para `90d`/`1y`, cada item traz `previous` (comparação com a janela
 * anterior) ou `null` (sem atividade do tipo no período anterior).
 * `enabled` controla se dispara (só no próprio perfil).
 * staleTime 60s: idem summary/weekly/monthly.
 */
export function useStatsByType(period: StatsPeriod = "all", enabled = true) {
  return useQuery<StatsByTypeResponse>({
    queryKey: statsKeys.byType(period),
    queryFn: () => getStatsByType(period),
    enabled,
    staleTime: 60_000,
    retry: 1,
  });
}