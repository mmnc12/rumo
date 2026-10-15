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

// Otimista: DELETE e 204 (sem body), entao nao da pra confiar no retorno.
// Estrategia: onMutate atualiza o cache local; onError faz rollback;
// onSettled invalida pra reconciliar com o servidor.
export function useToggleLike(activityId: string) {
  const qc = useQueryClient();
  const key = socialKeys.likes(activityId);

  return useMutation({
    mutationFn: async (currentlyLiked: boolean) => {
      if (currentlyLiked) {
        await unlikeActivity(activityId);
      } else {
        await likeActivity(activityId); // 200 com LikeState (ignoramos)
      }
    },
    onMutate: async (currentlyLiked) => {
      await qc.cancelQueries({ queryKey: key });
      const previous = qc.getQueryData<LikeList>(key);

      qc.setQueryData<LikeList>(key, (old) => {
        if (!old) {
          return { count: currentlyLiked ? 0 : 1, liked_by_me: !currentlyLiked, users: [] };
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
      qc.invalidateQueries({ queryKey: ["feed"] });
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
    },
  });
}