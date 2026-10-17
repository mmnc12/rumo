import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { StatsPeriod } from "../types/api";

interface Props {
  items: StatsPeriod[] | undefined;
  isLoading: boolean;
  isError: boolean;
}

export function WeeklyChart({ items, isLoading, isError }: Props) {
  if (isLoading) {
    return (
      <div className="h-64 animate-pulse rounded-lg bg-gray-100" />
    );
  }

  if (isError || !items) {
    return (
      <p className="text-sm text-red-600">Erro ao carregar gráfico.</p>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg bg-white shadow-sm">
        <p className="text-sm text-gray-500">
          Sem dados nas últimas semanas.
        </p>
      </div>
    );
  }

  // Recharts espera dados num array de objetos. Convertemos distance_m → km
  // e formatamos o label do eixo X como "DD/MM".
  const data = items.map((p) => ({
    label: formatShortDate(p.period_start),
    km: p.total_distance_m / 1000,
    fullDate: p.period_start,
  }));

  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Distância por semana (km)
      </h3>
      <div style={{ height: "16rem" }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 12, fill: "#6b7280" }}
              axisLine={{ stroke: "#e5e7eb" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6b7280" }}
              axisLine={{ stroke: "#e5e7eb" }}
              tickLine={false}
              width={40}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: "1px solid #e5e7eb",
                fontSize: 12,
              }}
              formatter={(value) => [`${Number(value).toFixed(1)} km`, "Distância"]}
              labelFormatter={(label) => `Semana de ${label}`}
            />
            <Line
              type="monotone"
              dataKey="km"
              stroke="#f97316"
              strokeWidth={2}
              dot={{ r: 3, fill: "#f97316" }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

/** "2026-10-13" → "13/10" */
function formatShortDate(iso: string): string {
  const [, month, day] = iso.split("-");
  return `${day}/${month}`;
}