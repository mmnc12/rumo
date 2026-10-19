import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "../api/client";
import type { UserPublic } from "../types/api";

/** Busca usuários por username/full_name. Só dispara com q >= 2 chars. */
export function useUserSearch(q: string) {
  const trimmed = q.trim();
  return useQuery({
    queryKey: ["users", "search", trimmed],
    queryFn: () =>
      apiFetch<UserPublic[]>(
        `/users/search?q=${encodeURIComponent(trimmed)}&limit=20`,
      ),
    enabled: trimmed.length >= 2,
    staleTime: 30_000,
  });
}