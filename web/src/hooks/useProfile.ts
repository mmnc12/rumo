import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { updateMe, type UpdateMePayload } from "../api/auth";
import { getFollowers, getFollowing, getUser } from "../api/social";
import { useAuth } from "./useAuth";
import { socialKeys } from "./useSocial";

export function useFollowers(userId: string) {
  return useQuery({
    queryKey: socialKeys.followers(userId),
    queryFn: () => getFollowers(userId),
    staleTime: 30_000,
    enabled: !!userId,
  });
}

export function useFollowing(userId: string) {
  return useQuery({
    queryKey: socialKeys.following(userId),
    queryFn: () => getFollowing(userId),
    staleTime: 30_000,
    enabled: !!userId,
  });
}

/**
 * Retorna true se o usuario logado segue `targetUserId`.
 *
 * Nao existe GET /users/{id}/is-following no backend, entao inferimos
 * buscando a lista de "following" do proprio usuario e checando se o
 * alvo esta la. Custa 1 request extra, mas e simples e correto.
 */
export function useIsFollowing(targetUserId: string) {
  const { user } = useAuth();
  const meId = user?.id;

  const { data: following, ...rest } = useFollowing(meId ?? "");

  const isFollowing = !!(
    meId &&
    targetUserId &&
    meId !== targetUserId &&
    following?.some((u) => u.id === targetUserId)
  );

  const isSelf = !!meId && meId === targetUserId;

  return { isFollowing, isSelf, ...rest };
}

/**
 * Busca o perfil público de um usuário (username, full_name, is_active).
 *
 * staleTime 5 min: perfil público muda pouco (nome/username),
 * e o cache compartilhado evita refetch ao navegar entre feed→perfil→detalhe.
 * 404 (id inexistente) propaga como erro — o componente trata.
 */
export function useUser(userId: string | undefined) {
  return useQuery({
    queryKey: ["users", userId],
    queryFn: () => getUser(userId!),
    enabled: !!userId,
    staleTime: 5 * 60_000,
    retry: 1,
  });
}

// [Sessão 40] PUT /users/me — edição do próprio perfil.
//
// No onSuccess:
// 1. auth.setUser(updated) → atualiza o AuthContext em memória. Sem isso,
//    o modal de edição reaberto na mesma sessão mostraria dados velhos
//    (o `user` do useAuth é a fonte do pré-preenchimento).
// 2. invalidateQueries(["users", updated.id]) → o useUser(id) refaz
//    GET /users/{id} e o header do ProfilePage reflete o novo full_name.
//
// Não invalidamos ["users", undefined] nem outros — só o id do usuário
// logado. O cache de terceiros não muda.
export function useUpdateMe() {
  const auth = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UpdateMePayload) => updateMe(payload),
    onSuccess: (updated) => {
      auth.setUser(updated);
      queryClient.invalidateQueries({ queryKey: ["users", updated.id] });
    },
  });
}