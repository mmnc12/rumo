import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { ActivityCard } from "../components/ActivityCard";
import { useUserActivities } from "../hooks/useActivities";
import {
  useFollowers,
  useFollowing,
  useIsFollowing,
  useUser,
} from "../hooks/useProfile";
import { useFollowUser } from "../hooks/useSocial";
import { ApiError } from "../api/client";
import type { UserPublic } from "../types/api";

export default function ProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<"followers" | "following">("followers");

  const {
    data: profile,
    isLoading: loadingProfile,
    error: errorProfile,
  } = useUser(id);

  const {
    data: activities,
    isLoading: loadingActivities,
    error: errorActivities,
  } = useUserActivities(id);

  const {
    data: followers,
    isLoading: loadingFollowers,
    isError: errorFollowers,
  } = useFollowers(id ?? "");
  const {
    data: following,
    isLoading: loadingFollowing,
    isError: errorFollowing,
  } = useFollowing(id ?? "");

  const { isFollowing, isSelf } = useIsFollowing(id ?? "");
  const toggleFollow = useFollowUser(id ?? "");

  if (!id) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AppHeader />
        <main className="mx-auto max-w-4xl px-4 py-6">
          <p className="text-sm text-gray-500">Perfil inválido.</p>
        </main>
      </div>
    );
  }

  const list = tab === "followers" ? followers : following;
  const listLoading = tab === "followers" ? loadingFollowers : loadingFollowing;
  const listError = tab === "followers" ? errorFollowers : errorFollowing;

  // 403 ao listar atividades do alvo = user logado não segue.
  const activitiesForbidden =
    errorActivities instanceof ApiError && errorActivities.status === 403;

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />

      <main className="mx-auto max-w-4xl px-4 py-6">
        {/* Cabecalho do perfil */}
        <div className="rounded-lg bg-white p-6 shadow-sm">
          {loadingProfile && (
            <p className="text-sm text-gray-500">Carregando perfil…</p>
          )}

          {errorProfile && !loadingProfile && (
            <p className="text-sm text-red-600">Perfil não encontrado.</p>
          )}

          {profile && (
            <>
              <h1 className="text-xl font-semibold text-gray-900">
                @{profile.username}
              </h1>
              {profile.full_name && (
                <p className="mt-1 text-sm text-gray-500">
                  {profile.full_name}
                </p>
              )}

              {isSelf ? (
                <p className="mt-2 text-sm text-gray-400">Este é você.</p>
              ) : (
                <button
                  type="button"
                  onClick={() => toggleFollow.mutate(isFollowing)}
                  disabled={toggleFollow.isPending}
                  className={`mt-4 rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 ${
                    isFollowing
                      ? "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                      : "bg-rumo-500 text-white hover:bg-rumo-600"
                  }`}
                >
                  {toggleFollow.isPending
                    ? "…"
                    : isFollowing
                      ? "Deixar de seguir"
                      : "Seguir"}
                </button>
              )}
            </>
          )}
        </div>

        {/* Atividades */}
        <section className="mt-6">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">
            Atividades
          </h2>

          {loadingActivities && (
            <p className="text-sm text-gray-500">Carregando atividades…</p>
          )}

          {activitiesForbidden && (
            <div className="rounded-lg bg-white p-4 shadow-sm">
              <p className="text-sm text-gray-600">
                Siga{" "}
                <span className="font-medium text-gray-900">
                  @{profile?.username ?? "este usuário"}
                </span>{" "}
                pra ver as atividades dele(a).
              </p>
            </div>
          )}

          {errorActivities && !activitiesForbidden && (
            <p className="text-sm text-red-600">
              Erro ao carregar atividades.
            </p>
          )}

          {activities && activities.length === 0 && !activitiesForbidden && (
            <p className="text-sm text-gray-500">
              Nenhuma atividade registrada ainda.
            </p>
          )}

          {activities && activities.length > 0 && (
            <ul className="space-y-3">
              {activities.map((a) => (
                <li key={a.id}>
                  <ActivityCard activity={a} />
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Abas */}
        <div className="mt-8 border-b border-gray-200">
          <nav className="flex gap-4">
            <button
              type="button"
              onClick={() => setTab("followers")}
              className={`border-b-2 pb-2 text-sm font-medium transition ${
                tab === "followers"
                  ? "border-rumo-500 text-rumo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Seguidores {followers ? `(${followers.length})` : ""}
            </button>
            <button
              type="button"
              onClick={() => setTab("following")}
              className={`border-b-2 pb-2 text-sm font-medium transition ${
                tab === "following"
                  ? "border-rumo-500 text-rumo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Seguindo {following ? `(${following.length})` : ""}
            </button>
          </nav>
        </div>

        {/* Lista de followers/following */}
        <div className="mt-4">
          {listLoading && (
            <p className="text-sm text-gray-500">Carregando…</p>
          )}

          {listError && (
            <p className="text-sm text-red-600">
              Erro ao carregar a lista.
            </p>
          )}

          {list && list.length === 0 && (
            <p className="text-sm text-gray-500">
              {tab === "followers"
                ? "Ninguém segue esta pessoa ainda."
                : "Esta pessoa ainda não segue ninguém."}
            </p>
          )}

          {list && list.length > 0 && (
            <ul className="divide-y divide-gray-200 overflow-hidden rounded-lg bg-white shadow-sm">
              {list.map((u) => (
                <UserRow key={u.id} user={u} />
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}

function UserRow({ user }: { user: UserPublic }) {
  return (
    <li>
      <Link
        to={`/users/${user.id}`}
        className="flex items-center justify-between px-4 py-3 transition hover:bg-gray-50"
      >
        <div className="min-w-0">
          <p className="truncate font-medium text-gray-900">
            @{user.username}
          </p>
          {user.full_name && (
            <p className="truncate text-sm text-gray-500">{user.full_name}</p>
          )}
        </div>
        <span className="text-sm text-gray-400">→</span>
      </Link>
    </li>
  );
}