import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createComment,
  deleteComment,
  followUser,
  getActivityLikes,
  getComments,
  getFeed,
  likeActivity,
  unfollowUser,
  unlikeActivity,
} from "../api/social";
import { activitiesKeys } from "./useActivities";
import type { LikeList } from "../types/api";

export const socialKeys = {
  feed: (limit = 20, offset = 0) => ["feed", { limit, offset }] as const,
  likes: (activityId: string) => ["likes", activityId] as const,
  comments: (activityId: string) => ["comments", activityId] as const,
  followers: (userId: string) => ["followers", userId] as const,
  following: (userId: string) => ["following", userId] as const,
};

export function useFeed(limit = 20, offset = 0) {
  return useQuery({
    queryKey: socialKeys.feed(limit, offset),
    queryFn: () => getFeed(limit, offset),
    staleTime: 30_000,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}

export function useActivityLikes(activityId: string) {
  return useQuery({
    queryKey: socialKeys.likes(activityId),
    queryFn: () => getActivityLikes(activityId),
    staleTime: 30_000,
    enabled: !!activityId,
  });
}

// Otimista: POST devolve LikeState (200); DELETE e 204 sem body.
// Estrategia: onMutate atualiza o cache local; onError faz rollback;
// onSettled invalida SO o cache de ["likes", id] (o feed nao tem
// contagem de likes, entao invalidar o feed so causa refetch inutil).
export function useToggleLike(activityId: string) {
  const qc = useQueryClient();
  const key = socialKeys.likes(activityId);

  return useMutation({
    mutationFn: async (currentlyLiked: boolean) => {
      if (currentlyLiked) {
        await unlikeActivity(activityId);
      } else {
        await likeActivity(activityId);
      }
    },
    onMutate: async (currentlyLiked) => {
      await qc.cancelQueries({ queryKey: key });
      const previous = qc.getQueryData<LikeList>(key);

      qc.setQueryData<LikeList>(key, (old) => {
        if (!old) {
          return {
            count: currentlyLiked ? 0 : 1,
            liked_by_me: !currentlyLiked,
            users: [],
          };
        }
        return {
          ...old,
          count: old.count + (currentlyLiked ? -1 : 1),
          liked_by_me: !currentlyLiked,
        };
      });

      return { previous };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.previous !== undefined) {
        qc.setQueryData(key, ctx.previous);
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: key });
    },
  });
}

export function useComments(activityId: string) {
  return useQuery({
    queryKey: socialKeys.comments(activityId),
    queryFn: () => getComments(activityId),
    staleTime: 30_000,
    enabled: !!activityId,
  });
}

export function useCreateComment(activityId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (content: string) => createComment(activityId, content),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: socialKeys.comments(activityId) });
    },
  });
}

export function useDeleteComment(activityId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (commentId: string) => deleteComment(commentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: socialKeys.comments(activityId) });
    },
  });
}

export function useFollowUser(targetUserId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (isFollowing: boolean) =>
      isFollowing ? unfollowUser(targetUserId) : followUser(targetUserId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["feed"] });
      qc.invalidateQueries({ queryKey: socialKeys.followers(targetUserId) });
      qc.invalidateQueries({ queryKey: socialKeys.following(targetUserId) });
      // Atualiza a lista de atividades no perfil do alvo logo apos
      // seguir/deixar de seguir — sem isso, a secao "Atividades"
      // so refletia a mudanca de permissao (403 -> 200) no reload.
      qc.invalidateQueries({ queryKey: activitiesKeys.lists() });
    },
  });
}