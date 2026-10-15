import { Link } from "react-router-dom";

import {
  activityEmoji,
  formatActivityType,
  formatDistance,
  formatDuration,
  formatPace,
  formatRelativeDate,
} from "../lib/format";
import type { Activity, UserPublic } from "../types/api";

interface ActivityCardProps {
  activity: Activity;
  /** Quando presente, mostra o autor acima do card (usado no feed). */
  author?: UserPublic;
}

export function ActivityCard({ activity, author }: ActivityCardProps) {
  const title = activity.title || formatActivityType(activity.activity_type);

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
          <span className="text-2xl">{activityEmoji(activity.activity_type)}</span>
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
        </div>
      </Link>
    </div>
  );
}