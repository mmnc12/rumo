/**
 * Wrapper de rotas autenticadas.
 * - Enquanto o AuthContext está no boot (isLoading), mostra tela de carregando.
 * - Se não logado, redireciona pra /login (guardando a rota original pra
 *   voltar depois do login).
 * - Se logado, renderiza o conteúdo.
 */

import { Navigate, useLocation } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "../hooks/useAuth";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Carregando…</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // `state.from` permite voltar pra onde o usuário queria depois do login.
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}