/**
 * Hooks de leitura de atividades via TanStack Query.
 *
 * Padrão de query keys: ["activities", params] e ["activities", id].
 * Isso permite invalidar só uma parte do cache depois de mutações
 * (ex: depois do upload do 13a.3 → invalidateQueries(["activities"])).
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getActivity, listActivities, uploadGpx } from "../api/activities";
import type {
  ListActivitiesParams,
  UploadGpxMeta,
} from "../api/activities";
import type { Activity } from "../types/api";

export const activitiesKeys = {
  all: ["activities"] as const,
  list: (params: ListActivitiesParams) =>
    ["activities", "list", params] as const,
  detail: (id: string) => ["activities", "detail", id] as const,
};

// ===== Queries =====

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

// ===== Mutations =====

/**
 * Upload de GPX. Ao sucesso, invalida a lista de atividades
 * (o card novo aparece no topo — backend ordena por started_at desc).
 */
export function useUploadGpx() {
  const qc = useQueryClient();
  return useMutation<Activity, Error, { file: File; meta?: UploadGpxMeta }>({
    mutationFn: ({ file, meta }) => uploadGpx(file, meta),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: activitiesKeys.all });
    },
  });
}