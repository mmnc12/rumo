/**
 * AuthContext — fonte única da verdade sobre "quem está logado".
 *
 * Responsabilidades:
 * - Guardar o UserResponse em memória
 * - Reidratar sessão ao carregar a página (chama /auth/me se tiver token)
 * - Expor login/register/logout pras telas
 *
 * Persistência do token fica em `api/client.ts` (localStorage), não aqui.
 * Aqui só orquestramos o ciclo de vida da sessão.
 */

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import * as authApi from "../api/auth";
import { clearToken, getToken, setToken } from "../api/client";
import type { LoginPayload, RegisterPayload } from "../api/auth";
import type { UserResponse } from "../types/api";

export interface AuthContextValue {
  user: UserResponse | null;
  /** true enquanto estamos checando se o token salvo ainda vale (boot do app). */
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Boot: se tem token salvo, tenta buscar /auth/me.
  // Se o token estiver expirado, apiFetch limpa e o user fica null.
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    let cancelled = false;
    authApi
      .getMe()
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        // Token inválido/expirado — apiFetch já limpou. Só garante estado limpo.
        if (!cancelled) setUser(null);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const { access_token } = await authApi.login(payload);
    setToken(access_token);
    const me = await authApi.getMe();
    setUser(me);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    await authApi.register(payload);
    // Registra e já loga automaticamente — UX comum em apps modernos.
    const { access_token } = await authApi.login({
      email: payload.email,
      password: payload.password,
    });
    setToken(access_token);
    const me = await authApi.getMe();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}