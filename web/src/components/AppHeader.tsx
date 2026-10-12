/**
 * Header global do app autenticado.
 * Reusado nas telas /activities, /upload, /activities/:id.
 * Simples por enquanto — botões de navegação chegam na Fase 2.
 */

import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function AppHeader() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/activities" className="text-xl font-bold text-rumo-500">
          Rumo
        </Link>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-gray-600 hidden sm:inline">
            {user?.username}
          </span>
          <button
            onClick={logout}
            className="text-gray-600 hover:text-rumo-600 transition"
          >
            Sair
          </button>
        </div>
      </div>
    </header>
  );
}