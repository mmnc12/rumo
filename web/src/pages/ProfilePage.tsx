import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { ActivityCard } from "../components/ActivityCard";
import { StatsCards } from "../components/StatsCards";
// [Sessão 14] Substitui os 4 gráficos por 1 componente parametrizado.
import {
  PeriodChart,
  type ChartPeriod,
  type ChartMetric,
} from "../components/PeriodChart";
import { useUserActivities } from "../hooks/useActivities";
import {
  useFollowers,
  useFollowing,
  useIsFollowing,
  useUser,
} from "../hooks/useProfile";
import {
  useStatsSummary,
  useStatsWeekly,
  useStatsMonthly,
  // [Sessão 14 — B1] Drill-down por tipo de atividade.
  useStatsByType,
} from "../hooks/useStats";
// [Sessão 17] Tipo do filtro de janela temporal do drill-down por tipo.
import type { StatsPeriod } from "../api/stats";
import { useFollowUser } from "../hooks/useSocial";
import { ApiError } from "../api/client";
// [Sessão 15 — B1] Reaproveita formatadores de lib/format.ts em vez de
// duplicar inline. Mesma decisão de "deixar o repo melhor do que estava".
// [Sessão 15 — B1b] +formatElevation pra coluna de elevação.
import {
  formatDistance,
  formatDuration,
  formatElevation,
  formatPace,
} from "../lib/format";
import type {
  ActivityType,
  UserPublic,
  StatsByTypeItem,
} from "../types/api";

// Filtros de tipo — "Tudo" = undefined (sem filtro no backend)
const TYPE_FILTERS: { label: string; value: ActivityType | undefined }[] = [
  { label: "Tudo", value: undefined },
  { label: "Corrida", value: "run" },
  { label: "Caminhada", value: "walk" },
  { label: "Pedal", value: "cycle" },
  { label: "Trilha", value: "hike" },
  { label: "Natação", value: "swim" },
];

// [Sessão 14 — B1] Rótulos pt-BR para a tabela por tipo.
const TYPE_LABELS: Record<ActivityType, string> = {
  run: "Corrida",
  walk: "Caminhada",
  cycle: "Pedal",
  hike: "Trilha",
  swim: "Natação",
  other: "Outro",
};

// [Sessão 15 — B1] Pace só faz sentido para atividades humanas de
// deslocamento a pé. Ciclismo/natação usam velocidade, não pace; "outro"
// é caixa-preta. Fora desses, a tabela mostra "—".
const PACE_TYPES: ReadonlySet<ActivityType> = new Set(["run", "walk", "hike"]);

// [Sessão 17] Rótulos pt-BR para o filtro de janela temporal do drill-down.
const PERIOD_FILTERS: { label: string; value: StatsPeriod }[] = [
  { label: "Todos", value: "all" },
  { label: "90 dias", value: "90d" },
  { label: "1 ano", value: "1y" },
];

export default function ProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<"followers" | "following">("followers");
  const [typeFilter, setTypeFilter] = useState<ActivityType | undefined>(
    undefined
  );
  // [Sessão 13] Semanal continua sendo o default.
  const [chartMode, setChartMode] = useState<ChartPeriod>("weekly");
  // [Sessão 13 — F] Distância continua sendo o default do segundo toggle.
  const [chartMetric, setChartMetric] = useState<ChartMetric>("distance");
  // [Sessão 17] Filtro de janela temporal do drill-down por tipo.
  const [byTypePeriod, setByTypePeriod] = useState<StatsPeriod>("all");

  const {
    data: profile,
    isLoading: loadingProfile,
    error: errorProfile,
  } = useUser(id);

  const {
    data: activitiesData,
    isLoading: loadingActivities,
    error: errorActivities,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useUserActivities(id);

  const {
    data: followers,
    isLoading: loadingFollowers,
    isError: errorFollowers,
  } = useFollowers(id ?? "");
  const {
    data: following,
    isLoading: loadingFollowing,
    isError: errorFollowing,
  } = useFollowing(id ?? "");

  const { isFollowing, isSelf } = useIsFollowing(id ?? "");
  const toggleFollow = useFollowUser(id ?? "");

  // Stats só no próprio perfil (endpoints /stats/* são do current_user)
  const summaryQuery = useStatsSummary(typeFilter, isSelf);
  const weeklyQuery = useStatsWeekly(8, typeFilter, isSelf);
  // [Sessão 13] Monthly só dispara quando o modo mensal está ativo.
  const monthlyQuery = useStatsMonthly(
    6,
    typeFilter,
    isSelf && chartMode === "monthly"
  );
  // [Sessão 14 — B1] Drill-down por tipo — sem filtro, sempre todos os tipos.
  // [Sessão 17] Agora aceita janela temporal (`byTypePeriod`).
  // [Sessão 18] Cada item pode trazer `previous` (janela anterior).
  const byTypeQuery = useStatsByType(byTypePeriod, isSelf);

  if (!id) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AppHeader />
        <main className="mx-auto max-w-4xl px-4 py-6">
          <p className="text-sm text-gray-500">Perfil inválido.</p>
        </main>
      </div>
    );
  }

  const list = tab === "followers" ? followers : following;
  const listLoading = tab === "followers" ? loadingFollowers : loadingFollowing;
  const listError = tab === "followers" ? errorFollowers : errorFollowing;

  const activitiesForbidden =
    errorActivities instanceof ApiError && errorActivities.status === 403;

  // useInfiniteQuery entrega { pages: Activity[][], pageParams } — achatamos
  // para renderizar numa lista só.
  const activities = activitiesData?.pages.flat() ?? [];

  // [Sessão 14] Escolhe a query ativa com base no chartMode, uma única vez.
  const activeChartQuery = chartMode === "weekly" ? weeklyQuery : monthlyQuery;

  // [Sessão 18] Comparação só faz sentido quando há janela anterior.
  const showPrevious = byTypePeriod !== "all";

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />

      <main className="mx-auto max-w-4xl px-4 py-6">
        {/* Cabecalho do perfil */}
        <div className="rounded-lg bg-white p-6 shadow-sm">
          {loadingProfile && (
            <p className="text-sm text-gray-500">Carregando perfil…</p>
          )}

          {errorProfile && !loadingProfile && (
            <p className="text-sm text-red-600">Perfil não encontrado.</p>
          )}

          {profile && (
            <>
              <h1 className="text-xl font-semibold text-gray-900">
                @{profile.username}
              </h1>
              {profile.full_name && (
                <p className="mt-1 text-sm text-gray-500">
                  {profile.full_name}
                </p>
              )}

              {isSelf ? (
                <p className="mt-2 text-sm text-gray-400">Este é você.</p>
              ) : (
                <button
                  type="button"
                  onClick={() => toggleFollow.mutate(isFollowing)}
                  disabled={toggleFollow.isPending}
                  className={`mt-4 rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 ${
                    isFollowing
                      ? "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                      : "bg-rumo-500 text-white hover:bg-rumo-600"
                  }`}
                >
                  {toggleFollow.isPending
                    ? "…"
                    : isFollowing
                      ? "Deixar de seguir"
                      : "Seguir"}
                </button>
              )}
            </>
          )}
        </div>

        {/* Stats — só no próprio perfil */}
        {isSelf && (
          <section className="mt-6">
            <div className="mb-3 flex flex-wrap gap-2">
              {TYPE_FILTERS.map((f) => {
                const active = typeFilter === f.value;
                return (
                  <button
                    key={f.label}
                    type="button"
                    onClick={() => setTypeFilter(f.value)}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                      active
                        ? "bg-rumo-500 text-white"
                        : "bg-white text-gray-600 hover:bg-gray-100"
                    }`}
                  >
                    {f.label}
                  </button>
                );
              })}
            </div>

            <StatsCards
              data={summaryQuery.data}
              isLoading={summaryQuery.isLoading}
              isError={summaryQuery.isError}
            />

            {/* [Sessão 13 + F] Dois toggles independentes. */}
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <div className="inline-flex rounded-lg bg-white p-1 shadow-sm">
                <button
                  type="button"
                  onClick={() => setChartMode("weekly")}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    chartMode === "weekly"
                      ? "bg-rumo-500 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  Semanal
                </button>
                <button
                  type="button"
                  onClick={() => setChartMode("monthly")}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    chartMode === "monthly"
                      ? "bg-rumo-500 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  Mensal
                </button>
              </div>

              <div className="inline-flex rounded-lg bg-white p-1 shadow-sm">
                <button
                  type="button"
                  onClick={() => setChartMetric("distance")}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    chartMetric === "distance"
                      ? "bg-rumo-500 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  Distância
                </button>
                <button
                  type="button"
                  onClick={() => setChartMetric("activities")}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    chartMetric === "activities"
                      ? "bg-rumo-500 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  Atividades
                </button>
              </div>
            </div>

            <div className="mt-4">
              {/* [Sessão 14] Um único componente cobre as 4 combinações. */}
              <PeriodChart
                period={chartMode}
                metric={chartMetric}
                items={activeChartQuery.data?.items}
                isLoading={activeChartQuery.isLoading}
                isError={activeChartQuery.isError}
              />
            </div>

            {/* [Sessão 14 — B1] Tabela de drill-down por tipo de atividade.
                Sempre mostra TODOS os tipos praticados (sem filtro) —
                o typeFilter acima continua afetando só cards/gráficos. */}
            {/* [Sessão 17] Header ganhou segmented control de janela temporal
                (Todos / 90 dias / 1 ano). O filtro afeta apenas esta tabela. */}
            {/* [Sessão 18] Quando period != "all", ganha coluna "vs. anterior"
                com delta (atividades / distância / elevação) em verde/vermelho. */}
            <div className="mt-6 rounded-lg bg-white p-4 shadow-sm">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-sm font-semibold text-gray-700">
                  Por tipo de atividade
                </h3>

                <div className="inline-flex rounded-lg bg-gray-50 p-1">
                  {PERIOD_FILTERS.map((p) => {
                    const active = byTypePeriod === p.value;
                    return (
                      <button
                        key={p.value}
                        type="button"
                        onClick={() => setByTypePeriod(p.value)}
                        className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                          active
                            ? "bg-rumo-500 text-white"
                            : "text-gray-600 hover:bg-gray-100"
                        }`}
                      >
                        {p.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {byTypeQuery.isLoading && (
                <p className="text-sm text-gray-500">Carregando…</p>
              )}

              {byTypeQuery.isError && (
                <p className="text-sm text-red-600">
                  Erro ao carregar tabela por tipo.
                </p>
              )}

              {byTypeQuery.data && byTypeQuery.data.items.length === 0 && (
                <p className="text-sm text-gray-500">
                  Nenhuma atividade registrada ainda.
                </p>
              )}

              {byTypeQuery.data && byTypeQuery.data.items.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
                        <th className="py-2 pr-3 font-medium">Tipo</th>
                        <th className="py-2 pr-3 text-right font-medium">
                          Atividades
                        </th>
                        <th className="py-2 pr-3 text-right font-medium">
                          Distância
                        </th>
                        {/* [Sessão 15 — B1b] Nova coluna: elevação acumulada. */}
                        <th className="py-2 pr-3 text-right font-medium">
                          Elevação
                        </th>
                        <th className="py-2 pr-3 text-right font-medium">
                          Tempo
                        </th>
                        {/* [Sessão 15 — B1] Nova coluna: pace médio do tipo. */}
                        <th className="py-2 pr-3 text-right font-medium">
                          Pace médio
                        </th>
                        <th className="py-2 pr-3 text-right font-medium">
                          Calorias
                        </th>
                        {/* [Sessão 18] Delta vs. janela anterior. */}
                        {showPrevious && (
                          <th className="py-2 text-right font-medium">
                            vs. anterior
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {byTypeQuery.data.items.map((item) => {
                        const pace = computePace(item);
                        const showPace = PACE_TYPES.has(item.activity_type);
                        return (
                          <tr key={item.activity_type}>
                            <td className="py-2 pr-3 font-medium text-gray-900">
                              {TYPE_LABELS[item.activity_type] ??
                                item.activity_type}
                            </td>
                            <td className="py-2 pr-3 text-right text-gray-700">
                              {item.total_activities}
                            </td>
                            <td className="py-2 pr-3 text-right text-gray-700">
                              {formatDistance(item.total_distance_m)}
                            </td>
                            {/* [Sessão 15 — B1b] Elevação acumulada do tipo. */}
                            <td className="py-2 pr-3 text-right text-gray-700">
                              {formatElevation(item.total_elevation_gain_m)}
                            </td>
                            <td className="py-2 pr-3 text-right text-gray-700">
                              {formatDuration(item.total_duration_s)}
                            </td>
                            <td className="py-2 pr-3 text-right text-gray-700">
                              {showPace ? formatPace(pace) : "—"}
                            </td>
                            <td className="py-2 pr-3 text-right text-gray-700">
                              {item.total_calories} kcal
                            </td>
                            {/* [Sessão 18] Delta vs. janela anterior. */}
                            {showPrevious && (
                              <td className="py-2 text-right align-top">
                                <PreviousDelta item={item} />
                              </td>
                            )}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Atividades */}
        <section className="mt-6">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">
            Atividades
          </h2>

          {loadingActivities && (
            <p className="text-sm text-gray-500">Carregando atividades…</p>
          )}

          {activitiesForbidden && (
            <div className="rounded-lg bg-white p-4 shadow-sm">
              <p className="text-sm text-gray-600">
                Siga{" "}
                <span className="font-medium text-gray-900">
                  @{profile?.username ?? "este usuário"}
                </span>{" "}
                pra ver as atividades dele(a).
              </p>
            </div>
          )}

          {errorActivities && !activitiesForbidden && (
            <p className="text-sm text-red-600">
              Erro ao carregar atividades.
            </p>
          )}

          {!loadingActivities && !errorActivities && activities.length === 0 && (
            <p className="text-sm text-gray-500">
              Nenhuma atividade registrada ainda.
            </p>
          )}

          {activities.length > 0 && (
            <>
              <ul className="space-y-3">
                {activities.map((a) => (
                  <li key={a.id}>
                    <ActivityCard activity={a} />
                  </li>
                ))}
              </ul>

              {hasNextPage && (
                <div className="mt-4 text-center">
                  <button
                    type="button"
                    onClick={() => fetchNextPage()}
                    disabled={isFetchingNextPage}
                    className="rounded-lg bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:opacity-50"
                  >
                    {isFetchingNextPage ? "Carregando…" : "Carregar mais"}
                  </button>
                </div>
              )}
            </>
          )}
        </section>

        {/* Abas */}
        <div className="mt-8 border-b border-gray-200">
          <nav className="flex gap-4">
            <button
              type="button"
              onClick={() => setTab("followers")}
              className={`border-b-2 pb-2 text-sm font-medium transition ${
                tab === "followers"
                  ? "border-rumo-500 text-rumo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Seguidores {followers ? `(${followers.length})` : ""}
            </button>
            <button
              type="button"
              onClick={() => setTab("following")}
              className={`border-b-2 pb-2 text-sm font-medium transition ${
                tab === "following"
                  ? "border-rumo-500 text-rumo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Seguindo {following ? `(${following.length})` : ""}
            </button>
          </nav>
        </div>

        {/* Lista de followers/following */}
        <div className="mt-4">
          {listLoading && (
            <p className="text-sm text-gray-500">Carregando…</p>
          )}

          {listError && (
            <p className="text-sm text-red-600">
              Erro ao carregar a lista.
            </p>
          )}

          {list && list.length === 0 && (
            <p className="text-sm text-gray-500">
              {tab === "followers"
                ? "Ninguém segue esta pessoa ainda."
                : "Esta pessoa ainda não segue ninguém."}
            </p>
          )}

          {list && list.length > 0 && (
            <ul className="divide-y divide-gray-200 overflow-hidden rounded-lg bg-white shadow-sm">
              {list.map((u) => (
                <UserRow key={u.id} user={u} />
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}

function UserRow({ user }: { user: UserPublic }) {
  return (
    <li>
      <Link
        to={`/users/${user.id}`}
        className="flex items-center justify-between px-4 py-3 transition hover:bg-gray-50"
      >
        <div className="min-w-0">
          <p className="truncate font-medium text-gray-900">
            @{user.username}
          </p>
          {user.full_name && (
            <p className="truncate text-sm text-gray-500">{user.full_name}</p>
          )}
        </div>
        <span className="text-sm text-gray-400">→</span>
      </Link>
    </li>
  );
}

// [Sessão 15 — B1] Pace médio do tipo, em segundos por km.
// Retorna null quando não há distância registrada (evita divisão por zero);
// formatPace(null) já devolve "—".
function computePace(item: {
  total_duration_s: number;
  total_distance_m: number;
}): number | null {
  if (item.total_distance_m <= 0) return null;
  return item.total_duration_s / (item.total_distance_m / 1000);
}

// [Sessão 18] Bloco de delta vs. janela imediatamente anterior.
// Mostra 3 métricas (atividades, distância, elevação) em linhas curtas.
// `previous === null` → "—" (tipo não existia na janela anterior).
function PreviousDelta({ item }: { item: StatsByTypeItem }) {
  if (!item.previous) {
    return <span className="text-xs text-gray-400">—</span>;
  }
  return (
    <div className="space-y-0.5 text-xs leading-tight">
      <DeltaLine
        label="Ativ."
        current={item.total_activities}
        previous={item.previous.total_activities}
      />
      <DeltaLine
        label="Dist."
        current={item.total_distance_m}
        previous={item.previous.total_distance_m}
        formatter={formatDistance}
      />
      <DeltaLine
        label="Elev."
        current={item.total_elevation_gain_m}
        previous={item.previous.total_elevation_gain_m}
        formatter={formatElevation}
      />
    </div>
  );
}

// [Sessão 18] Uma linha de delta: "label ±abs (±pct%)" colorido.
// Verde = subiu, vermelho = desceu, cinza = igual. Percentual só quando
// `previous > 0` (percentual em relação a 0 é indefinido).
function DeltaLine({
  label,
  current,
  previous,
  formatter,
}: {
  label: string;
  current: number;
  previous: number;
  formatter?: (n: number) => string;
}) {
  const delta = current - previous;
  const fmt = formatter ?? ((n: number) => `${Math.round(n)}`);
  const sign = delta > 0 ? "+" : delta < 0 ? "−" : "";
  const abs = Math.abs(delta);
  const pct = previous > 0 ? Math.round((delta / previous) * 100) : null;
  const color =
    delta > 0
      ? "text-green-600"
      : delta < 0
        ? "text-red-600"
        : "text-gray-400";
  const pctText = pct !== null ? ` (${sign}${Math.abs(pct)}%)` : "";

  return (
    <div className={color}>
      {label} {sign}
      {fmt(abs)}
      {pctText}
    </div>
  );
}