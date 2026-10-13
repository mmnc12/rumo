import { Link } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function AppHeader() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <Link
          to="/activities"
          className="text-lg font-semibold text-rumo-600 hover:text-rumo-700"
        >
          Rumo
        </Link>

        <div className="flex items-center gap-3">
          <Link
            to="/upload"
            className="rounded-lg bg-rumo-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-rumo-600"
          >
            + Enviar
          </Link>

          {user && (
            <span className="hidden text-sm text-gray-500 sm:inline">
              {user.username}
            </span>
          )}

          <button
            type="button"
            onClick={logout}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            Sair
          </button>
        </div>
      </div>
    </header>
  );
}