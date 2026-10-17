import { apiFetch } from "./client";
import type {
  Comment,
  FeedItem,
  LikeList,
  LikeState,
  UserPublic,
} from "../types/api";

// ===== Feed =====
export function getFeed(limit = 20, offset = 0): Promise<FeedItem[]> {
  const qs = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch<FeedItem[]>(`/feed?${qs}`);
}

// ===== Likes =====
// POST devolve LikeStateResponse (200). DELETE e 204 sem body.
export function likeActivity(activityId: string): Promise<LikeState> {
  return apiFetch<LikeState>(`/activities/${activityId}/like`, { method: "POST" });
}

export function unlikeActivity(activityId: string): Promise<void> {
  return apiFetch<void>(`/activities/${activityId}/like`, { method: "DELETE" });
}

export function getActivityLikes(
  activityId: string,
  limit = 50,
  offset = 0,
): Promise<LikeList> {
  const qs = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch<LikeList>(`/activities/${activityId}/likes?${qs}`);
}

// ===== Comentarios =====
export function getComments(
  activityId: string,
  limit = 50,
  offset = 0,
): Promise<Comment[]> {
  const qs = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch<Comment[]>(`/activities/${activityId}/comments?${qs}`);
}

export function createComment(activityId: string, content: string): Promise<Comment> {
  return apiFetch<Comment>(`/activities/${activityId}/comments`, {
    method: "POST",
    body: { content },
  });
}

export function deleteComment(commentId: string): Promise<void> {
  return apiFetch<void>(`/comments/${commentId}`, { method: "DELETE" });
}

// ===== Follows =====
export function followUser(userId: string): Promise<void> {
  return apiFetch<void>(`/users/${userId}/follow`, { method: "POST" });
}

export function unfollowUser(userId: string): Promise<void> {
  return apiFetch<void>(`/users/${userId}/follow`, { method: "DELETE" });
}

export function getFollowers(
  userId: string,
  limit = 20,
  offset = 0,
): Promise<UserPublic[]> {
  const qs = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch<UserPublic[]>(`/users/${userId}/followers?${qs}`);
}

export function getFollowing(
  userId: string,
  limit = 20,
  offset = 0,
): Promise<UserPublic[]> {
  const qs = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch<UserPublic[]>(`/users/${userId}/following?${qs}`);
}

// ===== Perfil público (13b.7) =====
export function getUser(userId: string): Promise<UserPublic> {
  return apiFetch<UserPublic>(`/users/${userId}`);
}