import { useQuery } from "@tanstack/react-query";

import { getStatsSummary, getStatsWeekly } from "../api/stats";
import type { StatsSummary, StatsWeeklyResponse } from "../types/api";

// ===== Query keys =====

export const statsKeys = {
  all: ["stats"] as const,
  summary: (activityType?: string) =>
    [...statsKeys.all, "summary", activityType ?? "all"] as const,
  weekly: (weeks: number, activityType?: string) =>
    [...statsKeys.all, "weekly", weeks, activityType ?? "all"] as const,
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