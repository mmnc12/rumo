import { Link } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { ActivityCard } from "../components/ActivityCard";
import { useAuth } from "../hooks/useAuth";
import { useFeed } from "../hooks/useSocial";

export default function FeedPage() {
  const { user } = useAuth();
  const {
    data,
    isLoading,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useFeed();

  // useInfiniteQuery entrega { pages: FeedItem[][], pageParams } — achatamos
  // para renderizar numa lista só. Cada página já vem com author aninhado.
  const items = data?.pages.flat() ?? [];

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />

      <main className="mx-auto max-w-4xl px-4 py-6">
        <h1 className="mb-4 text-xl font-semibold text-gray-900">Feed</h1>

        {isLoading && (
          <p className="text-sm text-gray-500">Carregando feed…</p>
        )}

        {isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Erro ao carregar o feed: {error.message}
          </div>
        )}

        {!isLoading && !isError && items.length === 0 && (
          <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
            <p className="text-gray-700">Nada por aqui ainda.</p>
            <p className="mt-1 text-sm text-gray-500">
              Siga alguém pra ver as atividades deles no feed.
            </p>
            {user && (
              <Link
                to={`/users/${user.id}`}
                className="mt-4 inline-block rounded-lg bg-rumo-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-rumo-600"
              >
                Ver meu perfil
              </Link>
            )}
          </div>
        )}

        {!isLoading && !isError && items.length > 0 && (
          <>
            <ul className="space-y-3">
              {items.map((item) => (
                <li key={item.id}>
                  <ActivityCard activity={item} author={item.author} />
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
      </main>
    </div>
  );
}