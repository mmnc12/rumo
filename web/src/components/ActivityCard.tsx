/**
 * Card de uma atividade na lista.
 * Mostra: emoji do tipo, título, data relativa, distância, pace, duração.
 *
 * Reutilizável: recebe um `Activity` e um `onClick` opcional. Se não tiver
 * onClick, vira um <Link> pra /activities/:id.
 */

import { Link } from "react-router-dom";
import type { Activity } from "../types/api";
import {
  activityEmoji,
  formatActivityType,
  formatDistance,
  formatDuration,
  formatPace,
  formatRelativeDate,
} from "../lib/format";

interface Props {
  activity: Activity;
}

export function ActivityCard({ activity }: Props) {
  const title = activity.title?.trim() || formatActivityType(activity.activity_type);

  return (
    <Link
      to={`/activities/${activity.id}`}
      className="block bg-white rounded-lg shadow-sm hover:shadow-md transition p-4"
    >
      <div className="flex items-start gap-3">
        <div className="text-3xl leading-none">{activityEmoji(activity.activity_type)}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="font-semibold text-gray-900 truncate">{title}</h3>
            <span className="text-xs text-gray-500 whitespace-nowrap">
              {formatRelativeDate(activity.started_at)}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            {formatActivityType(activity.activity_type)}
          </p>

          <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
            <div>
              <div className="text-xs text-gray-500">Distância</div>
              <div className="font-medium">
                {formatDistance(activity.distance_m)}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Pace</div>
              <div className="font-medium">
                {formatPace(activity.avg_pace_s_per_km)}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Duração</div>
              <div className="font-medium">
                {formatDuration(activity.duration_s)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}