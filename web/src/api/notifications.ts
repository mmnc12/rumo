import { apiFetch } from "./client";
import type {
  Notification,
  UnreadCountResponse,
  MarkAllReadResponse,
} from "../types/api";

export function listNotifications(
  limit = 20,
  offset = 0
): Promise<Notification[]> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  return apiFetch<Notification[]>(`/notifications?${params.toString()}`);
}

export function getUnreadCount(): Promise<UnreadCountResponse> {
  return apiFetch<UnreadCountResponse>("/notifications/unread-count");
}

export function markNotificationRead(id: string): Promise<void> {
  return apiFetch<void>(`/notifications/${id}/read`, { method: "POST" });
}

export function markAllNotificationsRead(): Promise<MarkAllReadResponse> {
  return apiFetch<MarkAllReadResponse>("/notifications/read-all", {
    method: "POST",
  });
}