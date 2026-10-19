import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "../api/client";
import type { FeedItem } from "../types/api";

/**
 * Busca atividades por texto em title/description.
 *
 * Espelha o contrato de `useUserSearch`:
 * - Só dispara com q >= 2 chars (mesmo limiar do backend, min_length=2).
 * - staleTime 30s — usuário alterna entre abas sem refetch a cada troca.
 * - queryKey inclui o termo trimado: cada termo tem seu próprio cache slot.
 *
 * O backend já retorna FeedItem[] (com author aninhado) — a lista é
 * renderizada com <ActivityCard activity={item} author={item.author} />.
 */
export function useActivitySearch(q: string) {
  const trimmed = q.trim();
  return useQuery({
    queryKey: ["activities", "search", trimmed],
    queryFn: () =>
      apiFetch<FeedItem[]>(
        `/activities/search?q=${encodeURIComponent(trimmed)}&limit=20`,
      ),
    enabled: trimmed.length >= 2,
    staleTime: 30_000,
  });
}