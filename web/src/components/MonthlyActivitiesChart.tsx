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

// [Sessão 13] Gráfico mensal de ATIVIDADES (contagem), par do MonthlyChart
// (que mostra DISTÂNCIA em km). Mesma estrutura visual, eixo Y inteiro.
interface Props {
  items: StatsPeriod[] | undefined;
  isLoading: boolean;
  isError: boolean;
}

export function MonthlyActivitiesChart({ items, isLoading, isError }: Props) {
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
          Sem dados nos últimos meses.
        </p>
      </div>
    );
  }

  // [Sessão 13] Contagem pura — sem conversão de unidade. Eixo X em MM/YYYY
  // porque cada ponto agrega o mês inteiro.
  const data = items.map((p) => ({
    label: formatMonthLabel(p.period_start),
    count: p.total_activities,
    fullDate: p.period_start,
  }));

  // Teto do eixo Y: pelo menos 5 pra não ficar espremido quando todos os
  // valores são 0/1/2. Arredonda pra cima (ex.: max=3 → 5; max=7 → 8).
  const maxCount = Math.max(...data.map((d) => d.count), 0);
  const yMax = Math.max(5, Math.ceil((maxCount + 1) / 5) * 5);

  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Atividades por mês
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
              domain={[0, yMax]}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: "1px solid #e5e7eb",
                fontSize: 12,
              }}
              formatter={(value) => {
                const n = Number(value);
                return [`${n} ${n === 1 ? "atividade" : "atividades"}`, "Total"];
              }}
              labelFormatter={(label) => `Mês de ${label}`}
            />
            <Line
              type="monotone"
              dataKey="count"
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

/**
 * "2026-11-01" → "11/2026".
 * O backend sempre entrega o primeiro dia do mês (YYYY-MM-01).
 */
function formatMonthLabel(iso: string): string {
  const [year, month] = iso.split("-");
  return `${month}/${year}`;
}