/**
 * Hooks de leitura de atividades via TanStack Query.
 *
 * Padrão de query keys: ["activities", params] e ["activities", id].
 * Isso permite invalidar só uma parte do cache depois de mutações
 * (ex: depois do upload do 13a.3 → invalidateQueries(["activities"])).
 */

import { useQuery } from "@tanstack/react-query";
import { getActivity, listActivities } from "../api/activities";
import type { ListActivitiesParams } from "../api/activities";

export const activitiesKeys = {
  all: ["activities"] as const,
  list: (params: ListActivitiesParams) =>
    ["activities", "list", params] as const,
  detail: (id: string) => ["activities", "detail", id] as const,
};

export function useActivities(params: ListActivitiesParams = {}) {
  return useQuery({
    queryKey: activitiesKeys.list(params),
    queryFn: () => listActivities(params),
  });
}

export function useActivity(id: string | undefined) {
  return useQuery({
    queryKey: activitiesKeys.detail(id ?? ""),
    queryFn: () => getActivity(id!),
    enabled: !!id, // não roda se id for undefined
  });
}