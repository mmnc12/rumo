import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { useDebounce } from "../hooks/useDebounce";
import { useUserSearch } from "../hooks/useUserSearch";

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQ = searchParams.get("q") ?? "";

  const [query, setQuery] = useState(initialQ);
  const debouncedQuery = useDebounce(query, 300);
  const { data, isPending, isError, error } = useUserSearch(debouncedQuery);

  // Sincroniza o termo debounced com a URL (deep-link / refresh).
  // replace:true evita encher o histórico a cada keystroke.
  useEffect(() => {
    const next = debouncedQuery.trim();
    const current = searchParams.get("q") ?? "";
    if (next === current) return;
    if (next.length === 0) {
      setSearchParams({}, { replace: true });
    } else {
      setSearchParams({ q: next }, { replace: true });
    }
  }, [debouncedQuery, searchParams, setSearchParams]);

  const tooShort = debouncedQuery.trim().length < 2;

  return (
    <div className="mx-auto max-w-2xl px-4 py-6">
      <div className="mb-4">
        <Link to="/feed" className="text-sm text-rumo-600 hover:underline">
          ← Voltar
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-gray-900">
          Buscar usuários
        </h1>
      </div>

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Username ou nome (mín. 2 caracteres)"
        autoFocus
        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-rumo-500 focus:ring-2 focus:ring-rumo-100"
      />

      <div className="mt-4">
        {tooShort && (
          <p className="text-sm text-gray-500">
            Digite ao menos 2 caracteres para buscar.
          </p>
        )}

        {!tooShort && isPending && (
          <p className="text-sm text-rumo-400">Buscando…</p>
        )}

        {!tooShort && isError && (
          <p className="text-sm text-red-600">
            Erro ao buscar:{" "}
            {error instanceof Error ? error.message : "tente novamente"}
          </p>
        )}

        {!tooShort && data && data.length === 0 && (
          <p className="text-sm text-gray-500">Nenhum usuário encontrado.</p>
        )}

        {data && data.length > 0 && (
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
                      <p className="truncate text-sm text-gray-500">
                        {u.full_name}
                      </p>
                    )}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}