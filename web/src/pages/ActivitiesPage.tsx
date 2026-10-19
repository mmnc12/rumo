import { Link } from "react-router-dom";
import { AppHeader } from "../components/AppHeader";
import { ActivityCard } from "../components/ActivityCard";
import { useActivities } from "../hooks/useActivities";

export default function ActivitiesPage() {
  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useActivities({ limit: 20 });

  // useInfiniteQuery entrega { pages: Activity[][], pageParams } — achatamos
  // para renderizar numa lista só. A ordem (mais recente primeiro) é a
  // ordem que o backend devolve.
  const activities = data?.pages.flat() ?? [];

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />

      <main className="max-w-2xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-lg font-semibold text-gray-900">
            Minhas atividades
          </h1>
          <Link
            to="/upload"
            className="text-sm bg-rumo-500 hover:bg-rumo-600 text-white px-3 py-1.5 rounded transition"
          >
            + Subir GPX
          </Link>
        </div>

        {isLoading && (
          <div className="text-center text-gray-500 py-12">Carregando…</div>
        )}

        {isError && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-3">
            Erro ao carregar atividades:{" "}
            {error instanceof Error ? error.message : "desconhecido"}
            <button
              onClick={() => refetch()}
              className="ml-2 underline hover:no-underline"
            >
              Tentar de novo
            </button>
          </div>
        )}

        {!isLoading && !isError && activities.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <div className="text-5xl mb-3">🏃</div>
            <h2 className="font-semibold text-gray-900 mb-1">
              Nenhuma atividade ainda
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Suba seu primeiro GPX pra começar.
            </p>
            <Link
              to="/upload"
              className="inline-block bg-rumo-500 hover:bg-rumo-600 text-white px-4 py-2 rounded transition"
            >
              Subir GPX
            </Link>
          </div>
        )}

        {!isLoading && !isError && activities.length > 0 && (
          <>
            <div className="space-y-3">
              {activities.map((a) => (
                <ActivityCard key={a.id} activity={a} />
              ))}
            </div>

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
      </main>
    </div>
  );
}