import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead,
} from "../api/notifications";

export const notificationsKeys = {
  all: ["notifications"] as const,
  list: (limit: number, offset: number) =>
    [...notificationsKeys.all, "list", { limit, offset }] as const,
  unreadCount: () => [...notificationsKeys.all, "unread-count"] as const,
};

export function useNotifications(limit = 20, offset = 0) {
  return useQuery({
    queryKey: notificationsKeys.list(limit, offset),
    queryFn: () => listNotifications(limit, offset),
    staleTime: 30_000,
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: notificationsKeys.unreadCount(),
    queryFn: getUnreadCount,
    staleTime: 30_000,
    refetchInterval: 30_000, // polling
    refetchOnWindowFocus: false,
  });
}

export function useMarkRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: notificationsKeys.all });
    },
  });
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => markAllNotificationsRead(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: notificationsKeys.all });
    },
  });
}