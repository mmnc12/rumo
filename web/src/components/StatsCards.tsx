import type { StatsSummary } from "../types/api";
import { formatDistance, formatDuration } from "../lib/format";

interface Props {
  data: StatsSummary | undefined;
  isLoading: boolean;
  isError: boolean;
}

export function StatsCards({ data, isLoading, isError }: Props) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-20 animate-pulse rounded-lg bg-gray-100"
          />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <p className="text-sm text-red-600">Erro ao carregar estatísticas.</p>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <StatCard
        label="Atividades"
        value={String(data.total_activities)}
      />
      <StatCard
        label="Distância"
        value={formatDistance(data.total_distance_m)}
      />
      <StatCard
        label="Tempo"
        value={formatDuration(data.total_duration_s)}
      />
      <StatCard
        label="Elevação"
        value={
          data.total_elevation_gain_m > 0
            ? `${Math.round(data.total_elevation_gain_m)} m`
            : "—"
        }
      />
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-gray-900">{value}</p>
    </div>
  );
}