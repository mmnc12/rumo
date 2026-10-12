/**
 * Placeholder do 13a.1 — só confirma que o login funcionou.
 * No 13a.2 isso vira a lista real de atividades.
 */

import { useAuth } from "../hooks/useAuth";

export default function ActivitiesPage() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <header className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-rumo-500">Rumo</h1>
          <button
            onClick={logout}
            className="text-sm text-gray-600 hover:text-rumo-600"
          >
            Sair
          </button>
        </header>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <p className="text-gray-700">
            Bem-vindo, <strong>{user?.full_name ?? user?.username}</strong>!
          </p>
          <p className="text-sm text-gray-500 mt-2">
            A lista de atividades chega no 13a.2.
          </p>
        </div>
      </div>
    </div>
  );
}