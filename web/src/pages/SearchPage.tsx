import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { ActivityResults } from "../components/ActivityResults";
import { UserResults } from "../components/UserResults";
import { useDebounce } from "../hooks/useDebounce";

type Tab = "users" | "activities";

const TABS: { id: Tab; label: string }[] = [
  { id: "users", label: "Usuários" },
  { id: "activities", label: "Atividades" },
];

function parseTab(value: string | null): Tab {
  return value === "activities" ? "activities" : "users";
}

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQ = searchParams.get("q") ?? "";
  const tab = parseTab(searchParams.get("tab"));

  const [query, setQuery] = useState(initialQ);
  const debouncedQuery = useDebounce(query, 300);

  // Sincroniza o termo debounced com a URL (deep-link / refresh).
  // replace:true evita encher o histórico a cada keystroke.
  // `tab` é preservado — trocar a aba não pode zerar a busca.
  useEffect(() => {
    const next = debouncedQuery.trim();
    const current = searchParams.get("q") ?? "";
    if (next === current) return;

    const nextParams = new URLSearchParams(searchParams);
    if (next.length === 0) {
      nextParams.delete("q");
    } else {
      nextParams.set("q", next);
    }
    setSearchParams(nextParams, { replace: true });
  }, [debouncedQuery, searchParams, setSearchParams]);

  function handleTabChange(next: Tab) {
    const nextParams = new URLSearchParams(searchParams);
    if (next === "users") {
      // Default da URL — não poluir com ?tab=users.
      nextParams.delete("tab");
    } else {
      nextParams.set("tab", next);
    }
    setSearchParams(nextParams, { replace: true });
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-6">
      <div className="mb-4">
        <Link to="/feed" className="text-sm text-rumo-600 hover:underline">
          ← Voltar
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-gray-900">Buscar</h1>
      </div>

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Buscar por usuário ou atividade (mín. 2 caracteres)"
        autoFocus
        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-rumo-500 focus:ring-2 focus:ring-rumo-100"
      />

      {/* Abas — aria-selected/role=tab pro leitor de tela navegar. */}
      <div
        role="tablist"
        aria-label="Tipo de busca"
        className="mt-4 flex gap-1 border-b border-gray-200"
      >
        {TABS.map((t) => {
          const active = t.id === tab;
          return (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => handleTabChange(t.id)}
              className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium transition ${
                active
                  ? "border-rumo-500 text-rumo-700"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.label}
            </button>
          );
        })}
      </div>

      <div className="mt-4">
        {tab === "users" ? (
          <UserResults query={debouncedQuery} />
        ) : (
          <ActivityResults query={debouncedQuery} />
        )}
      </div>
    </div>
  );
}