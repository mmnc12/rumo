import { useState } from "react";
import { Link } from "react-router-dom";

import {
  activityEmoji,
  formatActivityType,
  formatDistance,
  formatDuration,
  formatPace,
  formatRelativeDate,
} from "../lib/format";
import { useToggleLike } from "../hooks/useSocial";
import type { Activity, UserPublic } from "../types/api";

interface ActivityCardProps {
  activity: Activity;
  /** Quando presente, mostra o autor acima do card (usado no feed). */
  author?: UserPublic;
}

export function ActivityCard({ activity, author }: ActivityCardProps) {
  const title = activity.title || formatActivityType(activity.activity_type);

  // Estado local do like. Como o feed nao traz contagem nem "curti por mim",
  // o coracao comeca vazio e so reflete o que o usuario fez nesta sessao.
  // No detalhe (13b.5) a gente busca GET /likes e reflete corretamente.
  const [liked, setLiked] = useState(false);
  const toggleLike = useToggleLike(activity.id);

  function handleLike(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    const next = !liked;
    setLiked(next);
    toggleLike.mutate(next, {
      onError: () => setLiked(!next), // rollback local se o backend falhar
    });
  }

  return (
    <div>
      {author && (
        <div className="mb-1 flex items-center gap-2 px-1 text-sm text-gray-600">
          <Link
            to={`/users/${author.id}`}
            className="font-medium text-gray-800 hover:text-rumo-600"
          >
            @{author.username}
          </Link>
          {author.full_name && (
            <span className="text-gray-400">· {author.full_name}</span>
          )}
        </div>
      )}

      <Link
        to={`/activities/${activity.id}`}
        className="block rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow p-4"
      >
        <div className="flex items-start gap-3">
          {/* Thumbnail lateral (bloco 17b frontend). Dentro do <Link> do card —
              sem <Link> aninhado, o clique herda a navegacao do pai. */}
          {activity.cover_photo_url && (
            <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-lg">
              <img
                src={activity.cover_photo_url}
                alt={title}
                loading="lazy"
                decoding="async"
                className="h-full w-full object-cover"
              />
              {activity.photo_count > 1 && (
                <span className="absolute bottom-1 right-1 rounded bg-black/60 px-1.5 py-0.5 text-[10px] font-medium text-white">
                  {activity.photo_count}
                </span>
              )}
            </div>
          )}

          <span className="text-2xl">
            {activityEmoji(activity.activity_type)}
          </span>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">{title}</h3>
            <p className="text-sm text-gray-500">
              {formatRelativeDate(activity.started_at)}
            </p>
            <div className="flex gap-4 mt-2 text-sm text-gray-700">
              <span>{formatDistance(activity.distance_m)}</span>
              <span>{formatDuration(activity.duration_s)}</span>
              <span>{formatPace(activity.avg_pace_s_per_km)}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLike}
            disabled={toggleLike.isPending}
            aria-label={liked ? "Remover like" : "Curtir"}
            className="ml-2 shrink-0 rounded-full p-1 transition hover:bg-gray-100 disabled:opacity-50"
          >
            <HeartIcon filled={liked} />
          </button>
        </div>
      </Link>
    </div>
  );
}

function HeartIcon({ filled }: { filled: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={filled ? 0 : 2}
      className={`h-5 w-5 ${filled ? "text-rumo-500" : "text-gray-400"}`}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
      />
    </svg>
  );
}