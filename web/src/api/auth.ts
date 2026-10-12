/**
 * Funções de API relacionadas a autenticação.
 * Cada função é uma "porta" tipada pra um endpoint do backend.
 */

import { apiFetch } from "./client";
import type { TokenResponse, UserResponse } from "../types/api";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  full_name?: string | null;
}

/**
 * POST /auth/login — o backend espera form-urlencoded (OAuth2PasswordRequestForm),
 * NÃO JSON. Por isso montamos manualmente o body.
 * O campo `username` do form é o email na prática.
 */
export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.set("username", payload.email);
  form.set("password", payload.password);

  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    rawBody: form,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    skipAuth: true,
  });
}

/**
 * POST /auth/register — cria usuário. Retorna o UserResponse (não o token).
 * Depois do registro, o front chama `login` automaticamente.
 */
export async function register(
  payload: RegisterPayload
): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/register", {
    method: "POST",
    body: payload,
    skipAuth: true,
  });
}

/**
 * GET /auth/me — retorna o usuário logado. Usado pra reidratar a sessão
 * quando a página recarrega (token já existe em localStorage).
 */
export async function getMe(): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/me");
}