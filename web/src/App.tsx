import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ActivitiesPage from "./pages/ActivitiesPage";

/**
 * Árvore de rotas do Rumo.
 * - /login, /register → públicas
 * - /activities → protegida (ProtectedRoute)
 * - / → redireciona pra /activities (o ProtectedRoute cuida do resto)
 * - * → 404 simples
 */
export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/activities"
          element={
            <ProtectedRoute>
              <ActivitiesPage />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/activities" replace />} />
        <Route
          path="*"
          element={
            <div className="min-h-screen flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-2xl font-bold">404</h1>
                <p className="text-gray-600">Página não encontrada.</p>
              </div>
            </div>
          }
        />
      </Routes>
    </AuthProvider>
  );
}