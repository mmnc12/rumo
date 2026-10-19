import { Link, useNavigate } from "react-router-dom";
import {
  useNotifications,
  useMarkRead,
  useMarkAllRead,
} from "../hooks/useNotifications";
import { useAuth } from "../hooks/useAuth";
import { formatRelativeDate } from "../lib/format";
import type { Notification } from "../types/api";

function notificationText(n: Notification): string {
  switch (n.type) {
    case "like":
      return "curtiu sua atividade";
    case "comment":
      return "comentou na sua atividade";
    case "follow":
      return "começou a seguir você";
  }
}

function notificationTarget(n: Notification): string | null {
  if (n.type === "follow") return `/users/${n.actor.id}`;
  if (n.activity) return `/activities/${n.activity.id}`;
  return null;
}

export default function NotificationsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { data: notifications, isLoading } = useNotifications(50, 0);
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  const hasUnread = notifications?.some((n) => !n.is_read) ?? false;

  function handleClick(n: Notification) {
    if (!n.is_read) markRead.mutate(n.id);
    const target = notificationTarget(n);
    if (target) navigate(target);
  }

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-rumo-900">Notificações</h1>
        {hasUnread && (
          <button
            type="button"
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
            className="rounded-md px-3 py-1.5 text-sm font-medium text-rumo-600 hover:bg-rumo-50 disabled:opacity-50"
          >
            Marcar todas como lidas
          </button>
        )}
      </div>

      {isLoading && (
        <p className="py-8 text-center text-sm text-rumo-400">Carregando...</p>
      )}

      {!isLoading && notifications?.length === 0 && (
        <div className="rounded-lg border border-rumo-100 bg-white py-12 text-center">
          <p className="text-sm text-rumo-500">
            Nenhuma notificação ainda. Interaja com a galera pra começar!
          </p>
        </div>
      )}

      {notifications && notifications.length > 0 && (
        <ul className="divide-y divide-rumo-100 overflow-hidden rounded-lg border border-rumo-100 bg-white">
          {notifications.map((n) => (
            <li key={n.id}>
              <button
                type="button"
                onClick={() => handleClick(n)}
                className={`flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-rumo-50 ${
                  n.is_read ? "bg-white" : "bg-rumo-50/60"
                }`}
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-rumo-100 text-sm font-semibold text-rumo-700">
                  {(n.actor.full_name ?? n.actor.username).charAt(0).toUpperCase()}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-rumo-900">
                    <span className="font-semibold">
                      {n.actor.full_name ?? `@${n.actor.username}`}
                    </span>{" "}
                    {notificationText(n)}
                    {n.activity?.title && (
                      <>
                        {" "}
                        <span className="text-rumo-600">
                          "{n.activity.title}"
                        </span>
                      </>
                    )}
                  </p>
                  <p className="mt-0.5 text-xs text-rumo-400">
                    {formatRelativeDate(n.created_at)}
                  </p>
                </div>
                {!n.is_read && (
                  <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-rumo-500" />
                )}
              </button>
            </li>
          ))}
        </ul>
      )}

      {user === null && (
        <p className="mt-4 text-center text-sm text-rumo-500">
          <Link to="/login" className="text-rumo-600 underline">
            Entre
          </Link>{" "}
          para ver suas notificações.
        </p>
      )}
    </div>
  );
}