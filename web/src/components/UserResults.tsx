import { Link } from "react-router-dom";

import { useUserSearch } from "../hooks/useUserSearch";

interface UserResultsProps {
  /** Termo já debounced (o debounce vive no SearchPage, não aqui). */
  query: string;
}

/**
 * Resultados da busca de usuários.
 *
 * Extraído do SearchPage pra manter a página só com estado/sync de URL
 * e cada aba com a sua própria lógica de render.
 */
export function UserResults({ query }: UserResultsProps) {
  const { data, isPending, isError, error } = useUserSearch(query);
  const tooShort = query.trim().length < 2;

  if (tooShort) {
    return (
      <p className="text-sm text-gray-500">
        Digite ao menos 2 caracteres para buscar.
      </p>
    );
  }

  if (isPending) {
    return <p className="text-sm text-rumo-400">Buscando…</p>;
  }

  if (isError) {
    return (
      <p className="text-sm text-red-600">
        Erro ao buscar:{" "}
        {error instanceof Error ? error.message : "tente novamente"}
      </p>
    );
  }

  if (!data || data.length === 0) {
    return <p className="text-sm text-gray-500">Nenhum usuário encontrado.</p>;
  }

  return (
    <ul className="divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white">
      {data.map((u) => (
        <li key={u.id}>
          <Link
            to={`/users/${u.id}`}
            className="flex items-center gap-3 px-4 py-3 transition hover:bg-gray-50"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-rumo-100 font-semibold text-rumo-700">
              {u.username.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="truncate font-medium text-gray-900">
                @{u.username}
              </p>
              {u.full_name && (
                <p className="truncate text-sm text-gray-500">{u.full_name}</p>
              )}
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}