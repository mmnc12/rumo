/**
 * Hook pra consumir o AuthContext.
 * Lança erro se usado fora do <AuthProvider> — pega bug de hierarquia cedo.
 */

import { useContext } from "react";
import { AuthContext, type AuthContextValue } from "../contexts/AuthContext";

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth precisa estar dentro de <AuthProvider>");
  }
  return ctx;
}