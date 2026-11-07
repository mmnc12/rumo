// [Sessão 14] Componente único para os 4 gráficos do perfil.
// Substitui WeeklyChart, MonthlyChart, WeeklyActivitiesChart e
// MonthlyActivitiesChart. As 4 combinações viraram 1 componente
// parametrizado por (period × metric).
//
// Regras de negócio preservadas 1:1 do código anterior:
// - metric="distance": eixo Y em km (toFixed 1 no tooltip).
// - metric="activities": eixo Y contagem inteira (allowDecimals=false),
//   domain [0, yMax] com yMax >= 5 e arredondado pra cima em múltiplos de 5.
// - period="weekly": label X "DD/MM", tooltip "Semana de DD/MM".
// - period="monthly": label X "MM/YYYY", tooltip "Mês de MM/YYYY".
// - Estados: loading (skeleton), erro, vazio (mensagens por período).

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

export type ChartPeriod = "weekly" | "monthly";
export type ChartMetric = "distance" | "activities";

interface Props {
  period: ChartPeriod;
  metric: ChartMetric;
  items: StatsPeriod[] | undefined;
  isLoading: boolean;
  isError: boolean;
}

export function PeriodChart({
  period,
  metric,
  items,
  isLoading,
  isError,
}: Props) {
  // ===== Estados de carregamento/erro/vazio =====

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
          {period === "weekly"
            ? "Sem dados nas últimas semanas."
            : "Sem dados nos últimos meses."}
        </p>
      </div>
    );
  }

  // ===== Preparação dos dados =====

  const formatLabel = period === "weekly" ? formatShortDate : formatMonthLabel;
  const tooltipLabel = period === "weekly" ? "Semana de" : "Mês de";

  const data = items.map((p) => ({
    label: formatLabel(p.period_start),
    value:
      metric === "distance"
        ? p.total_distance_m / 1000 // km
        : p.total_activities, // contagem
    fullDate: p.period_start,
  }));

  // [Sessão 14 — fix TS] yMax é number|null em vez de number|undefined pra
  // casar com o tipo AxisDomain do recharts sem cast. Só é usado quando
  // metric === "activities" (contagem inteira).
  const maxValue = Math.max(...data.map((d) => d.value), 0);
  const yMax: number | null =
    metric === "activities"
      ? Math.max(5, Math.ceil((maxValue + 1) / 5) * 5)
      : null;

  // [Sessão 14 — fix TS] recharts tipa `value` como ValueType|undefined;
  // em runtime nunca é undefined aqui (só 1 <Line>), mas o TS exige o
  // tratamento. Fallback "0" preserva a UX.
  const formatter = (value: unknown): [string, string] => {
    const n = Number(value ?? 0);
    if (metric === "distance") {
      return [`${n.toFixed(1)} km`, "Distância"];
    }
    return [`${n} ${n === 1 ? "atividade" : "atividades"}`, "Total"];
  };

  const title =
    metric === "distance"
      ? period === "weekly"
        ? "Distância por semana (km)"
        : "Distância por mês (km)"
      : period === "weekly"
        ? "Atividades por semana"
        : "Atividades por mês";

  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">{title}</h3>
      <div style={{ height: "16rem" }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 8, right: 8, left: -16, bottom: 0 }}
          >
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
              domain={yMax !== null ? [0, yMax] : undefined}
              allowDecimals={metric !== "activities"}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: "1px solid #e5e7eb",
                fontSize: 12,
              }}
              formatter={formatter}
              labelFormatter={(label) => `${tooltipLabel} ${label}`}
            />
            <Line
              type="monotone"
              dataKey="value"
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

/** "2026-10-13" → "13/10" (label semanal) */
function formatShortDate(iso: string): string {
  const [, month, day] = iso.split("-");
  return `${day}/${month}`;
}

/**
 * "2026-11-01" → "11/2026" (label mensal).
 * O backend sempre entrega o primeiro dia do mês (YYYY-MM-01).
 */
function formatMonthLabel(iso: string): string {
  const [year, month] = iso.split("-");
  return `${month}/${year}`;
}