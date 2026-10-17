import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  deleteActivity,
  getActivity,
  getActivityTrack,
  listActivities,
  uploadGpx,
} from "../api/activities";
import type { Activity, TrackResponse } from "../types/api";

// ===== Query keys =====

export const activitiesKeys = {
  all: ["activities"] as const,
  lists: () => [...activitiesKeys.all, "list"] as const,
  list: (params?: { limit?: number; offset?: number; userId?: string }) =>
    [...activitiesKeys.lists(), params] as const,
  details: () => [...activitiesKeys.all, "detail"] as const,
  detail: (id: string) => [...activitiesKeys.details(), id] as const,
  tracks: () => [...activitiesKeys.all, "track"] as const,
  track: (id: string) => [...activitiesKeys.tracks(), id] as const,
};

// ===== Lista =====

/**
 * Lista atividades do usuário autenticado (paginado).
 *
 * staleTime 30s: lista muda com frequência (uploads recentes),
 * mas não precisa refetch a cada focus.
 */
export function useActivities(params?: {
  limit?: number;
  offset?: number;
  userId?: string;
}) {
  return useQuery<Activity[]>({
    queryKey: activitiesKeys.list(params),
    queryFn: () => listActivities(params),
    staleTime: 30_000,
    retry: 1,
  });
}

/**
 * Lista atividades de um usuário específico (perfil público).
 *
 * `enabled: !!userId` evita disparar antes do id resolver.
 * Retorna 403 do backend se o usuário logado não segue o alvo —
 * o componente trata esse erro (mostra CTA "siga pra ver").
 */
export function useUserActivities(userId: string | undefined) {
  return useQuery<Activity[]>({
    queryKey: activitiesKeys.list({ userId }),
    queryFn: () => listActivities({ userId: userId! }),
    enabled: !!userId,
    staleTime: 30_000,
    retry: 1,
  });
}

// ===== Detalhe =====

/**
 * Busca uma atividade específica do usuário.
 *
 * `enabled: !!id` evita disparar a query quando o id ainda não resolveu.
 */
export function useActivity(id: string | undefined) {
  return useQuery<Activity>({
    queryKey: activitiesKeys.detail(id!),
    queryFn: () => getActivity(id!),
    enabled: !!id,
    staleTime: 30_000,
    retry: 1,
  });
}

// ===== Track (geometria pro mapa) =====

/**
 * Busca a geometria da rota de uma atividade.
 *
 * staleTime 5 min: a geometria de uma atividade nunca muda depois de criada
 * (não há edição de rota), então cache agressivo é seguro.
 */
export function useActivityTrack(id: string | undefined) {
  return useQuery<TrackResponse>({
    queryKey: activitiesKeys.track(id!),
    queryFn: () => getActivityTrack(id!),
    enabled: !!id,
    staleTime: 5 * 60_000,
    retry: 1,
  });
}

// ===== Upload =====

/**
 * Faz upload de um GPX e invalida a lista pra refletir a nova atividade.
 */
export function useUploadGpx() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      file,
      meta,
    }: {
      file: File;
      meta?: { title?: string; activity_type?: string; description?: string };
    }) => uploadGpx(file, meta),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: activitiesKeys.all });
    },
  });
}

// ===== Delete =====

/**
 * Remove uma atividade e invalida listas + caches de detalhe/track.
 */
export function useDeleteActivity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteActivity(id),
    onSuccess: (_data, id) => {
      // Invalida tudo relacionado a essa atividade (lista, detail, track)
      queryClient.invalidateQueries({ queryKey: activitiesKeys.all });
      queryClient.removeQueries({ queryKey: activitiesKeys.detail(id) });
      queryClient.removeQueries({ queryKey: activitiesKeys.track(id) });
    },
  });
}