import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

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
  // Lista infinita: a key não inclui offset (o offset é pageParam).
  // Inclui o userId para diferenciar "minhas" de "de outro usuário".
  list: (params?: { limit?: number; userId?: string }) =>
    [...activitiesKeys.lists(), params] as const,
  details: () => [...activitiesKeys.all, "detail"] as const,
  detail: (id: string) => [...activitiesKeys.details(), id] as const,
  tracks: () => [...activitiesKeys.all, "track"] as const,
  track: (id: string) => [...activitiesKeys.tracks(), id] as const,
};

// ===== Lista =====

/**
 * Lista atividades do usuário autenticado (paginado com "Carregar mais").
 *
 * useInfiniteQuery mantém as páginas já carregadas em cache e permite
 * fetchNextPage sem refazer as anteriores. getNextPageParam assume que
 * a API retorna list[T] puro (sem envelope): se a última página veio
 * cheia (=== limit), pode haver mais; se veio menor, é o fim.
 */
export function useActivities(params?: { limit?: number }) {
  const limit = params?.limit ?? 20;
  return useInfiniteQuery<Activity[]>({
    queryKey: activitiesKeys.list({ limit }),
    queryFn: ({ pageParam = 0 }) =>
      listActivities({ limit, offset: pageParam as number }),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      if (lastPage.length < limit) return undefined;
      return allPages.reduce((acc, p) => acc + p.length, 0);
    },
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
  const limit = 20;
  return useInfiniteQuery<Activity[]>({
    queryKey: activitiesKeys.list({ userId, limit }),
    queryFn: ({ pageParam = 0 }) =>
      listActivities({ userId: userId!, limit, offset: pageParam as number }),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      if (lastPage.length < limit) return undefined;
      return allPages.reduce((acc, p) => acc + p.length, 0);
    },
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
      queryClient.invalidateQueries({ queryKey: activitiesKeys.all });
      queryClient.removeQueries({ queryKey: activitiesKeys.detail(id) });
      queryClient.removeQueries({ queryKey: activitiesKeys.track(id) });
    },
  });
}