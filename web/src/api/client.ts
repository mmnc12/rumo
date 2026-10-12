/**
 * Cliente HTTP central do Rumo.
 *
 * Responsabilidades:
 * - Prefixar todas as requests com VITE_API_URL
 * - Injetar o JWT automaticamente (se existir em localStorage)
 * - Tratar erros da API de forma previsível (lançar ApiError)
 * - Lidar com respostas 204 (sem body)
 *
 * Por que não usar axios? fetch nativo + um wrapper resolve e evita uma
 * dependência extra. TanStack Query cuida de cache/retry/loading.
 */

const API_URL = import.meta.env.VITE_API_URL as string;

if (!API_URL) {
  throw new Error(
    "VITE_API_URL não está definida. Confira o .env.local (dev) ou as env vars do Vercel (prod)."
  );
}

const TOKEN_KEY = "rumo.token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Erro estruturado lançado por `apiFetch` quando a resposta não é 2xx.
 * O `status` permite tratamento específico (ex: 401 → logout automático).
 */
export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown, message?: string) {
    super(message ?? `Erro HTTP ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

type FetchOptions = Omit<RequestInit, "body"> & {
  body?: unknown;       // objeto → vira JSON automaticamente
  rawBody?: BodyInit;   // multipart/FormData → passa direto
  skipAuth?: boolean;   // para endpoints públicos (futuro)
};

export async function apiFetch<T>(
  path: string,
  options: FetchOptions = {}
): Promise<T> {
  const { body, rawBody, skipAuth, headers, ...rest } = options;

  const finalHeaders = new Headers(headers);

  // Só seta Content-Type se NÃO for FormData (o browser seta sozinho com boundary)
  if (body !== undefined && !(rawBody instanceof FormData)) {
    if (!finalHeaders.has("Content-Type")) {
      finalHeaders.set("Content-Type", "application/json");
    }
  }

  if (!skipAuth) {
    const token = getToken();
    if (token) {
      finalHeaders.set("Authorization", `Bearer ${token}`);
    }
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: finalHeaders,
    body:
      rawBody !== undefined
        ? rawBody
        : body !== undefined
        ? JSON.stringify(body)
        : undefined,
  });

  // 204 No Content — retorna undefined como T
  if (res.status === 204) {
    return undefined as T;
  }

  // Tenta parsear JSON de erro OU sucesso
  let payload: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!res.ok) {
    // FastAPI devolve { detail: "..." } ou { detail: [...] } (Pydantic)
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail: unknown }).detail
        : payload;

    // 401 → token inválido/expirado. Limpa pra forçar novo login.
    if (res.status === 401 && !skipAuth) {
      clearToken();
    }

    throw new ApiError(res.status, detail);
  }

  return payload as T;
}