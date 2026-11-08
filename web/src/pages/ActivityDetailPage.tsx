// [Sessão 11 — fix] toggle Mapa/Satélite no mapa do detalhe (igual mobile).
// [Sessão 13] Mapa extraído para components/RouteMap.tsx (reutilizável).
// [Sessão 21] Botões "Baixar CSV" e "Baixar GPX" no cabeçalho do detalhe.
// [Sessão 25] RouteMap carregado com React.lazy + Suspense (tira leaflet do chunk principal).

import { lazy, Suspense, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { CommentsSection } from "../components/CommentsSection";
import { LikeButton } from "../components/LikeButton";
import { PhotoGallery } from "../components/PhotoGallery";
import { PhotoUpload } from "../components/PhotoUpload";
// [Sessão 25] RouteMap agora entra via React.lazy — named export resolvido
// com `.then(m => ({ default: m.RouteMap }))` para o `lazy` aceitar.
const RouteMap = lazy(() =>
  import("../components/RouteMap").then((m) => ({ default: m.RouteMap })),
);
import { useAuth } from "../hooks/useAuth";
import {
  useActivity,
  useActivityTrack,
  useDeleteActivity,
} from "../hooks/useActivities";
import { useActivityPhotos, useDeletePhoto } from "../hooks/usePhotos";
import { downloadActivityExport } from "../api/activities";
import {
  activityEmoji,
  formatActivityType,
  formatCalories,
  formatDateTime,
  formatDistance,
  formatDuration,
  formatPace,
} from "../lib/format";

export default function ActivityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const { data: activity, isLoading, error } = useActivity(id);
  const { data: track } = useActivityTrack(id);
  const { data: photos } = useActivityPhotos(id);
  const deleteMutation = useDeleteActivity();
  const deletePhoto = useDeletePhoto(id ?? "");

  // [Sessão 21] Estado local por botão (evita acoplar dois downloads).
  const [busyCsv, setBusyCsv] = useState(false);
  const [busyGpx, setBusyGpx] = useState(false);

  async function handleDelete() {
    if (!id) return;
    if (!confirm("Tem certeza que quer apagar esta atividade?")) return;
    await deleteMutation.mutateAsync(id);
    navigate("/activities");
  }

  async function handleDownload(format: "csv" | "gpx") {
    if (!id) return;
    const setBusy = format === "csv" ? setBusyCsv : setBusyGpx;
    setBusy(true);
    try {
      await downloadActivityExport(id, format);
    } catch (err) {
      // ApiError tem .detail; mostramos o mais informativo que houver.
      const detail =
        err && typeof err === "object" && "detail" in err
          ? String((err as { detail: unknown }).detail)
          : "Não foi possível baixar o arquivo.";
      alert(detail);
    } finally {
      setBusy(false);
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AppHeader />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-gray-500">Carregando atividade…</p>
        </div>
      </div>
    );
  }

  if (error || !activity) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AppHeader />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600 mb-4">Atividade não encontrada.</p>
          <Link to="/activities" className="text-rumo-600 hover:underline">
            ← Voltar
          </Link>
        </div>
      </div>
    );
  }

  const isOwner = !!user && user.id === activity.user_id;
  const hasTrack = !!track && track.coordinates.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Cabeçalho */}
        <div className="mb-6">
          <Link
            to="/activities"
            className="text-sm text-rumo-600 hover:underline mb-2 inline-block"
          >
            ← Voltar
          </Link>

          {activity.author && (
            <p className="text-sm text-gray-500 mb-1">
              por{" "}
              <Link
                to={`/users/${activity.author.id}`}
                className="text-rumo-600 hover:underline font-medium"
              >
                @{activity.author.username}
              </Link>
            </p>
          )}

          <div className="flex items-start justify-between gap-2 flex-wrap">
            <h1 className="text-2xl font-bold flex items-center gap-2 min-w-0">
              <span>{activityEmoji(activity.activity_type)}</span>
              <span className="truncate">
                {activity.title || formatActivityType(activity.activity_type)}
              </span>
            </h1>
            {/* [Sessão 21] Botões de export — CSV sempre, GPX se houver rota.
                Ficam visíveis para dono e seguidor (backend aceita os dois). */}
            <div className="flex gap-2 shrink-0">
              <button
                type="button"
                onClick={() => handleDownload("csv")}
                disabled={busyCsv}
                className="text-xs px-3 py-1.5 rounded border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {busyCsv ? "Baixando…" : "Baixar CSV"}
              </button>
              {hasTrack && (
                <button
                  type="button"
                  onClick={() => handleDownload("gpx")}
                  disabled={busyGpx}
                  className="text-xs px-3 py-1.5 rounded border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {busyGpx ? "Baixando…" : "Baixar GPX"}
                </button>
              )}
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {formatDateTime(activity.started_at)}
          </p>
        </div>

        {/* Mapa — [Sessão 13] extraído para RouteMap. O componente cuida do
            estado vazio ("Sem rota disponível…"), do toggle Mapa/Satélite
            e do fit bounds. [Sessão 25] Carregado via React.lazy; o fallback
            mantém a altura de 24rem (default do RouteMap) para não haver
            salto de layout enquanto o chunk do leaflet baixa. */}
        <Suspense
          fallback={
            <div
              className="mb-6 rounded-lg bg-gray-100 flex items-center justify-center"
              style={{ height: "24rem" }}
            >
              <p className="text-gray-500">Carregando mapa…</p>
            </div>
          }
        >
          <RouteMap track={track} className="mb-6" />
        </Suspense>

        {/* Fotos */}
        {(isOwner || (photos && photos.length > 0)) && (
          <section className="mb-6">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-700">Fotos</h2>
              {isOwner && id && <PhotoUpload activityId={id} />}
            </div>
            {photos && photos.length > 0 ? (
              <PhotoGallery
                photos={photos}
                canDelete={isOwner}
                onDelete={(photoId) => deletePhoto.mutate(photoId)}
              />
            ) : (
              isOwner && (
                <p className="text-sm text-gray-500">
                  Nenhuma foto ainda. Adicione a primeira.
                </p>
              )
            )}
          </section>
        )}

        {/* Like */}
        <div className="mb-6">
          <LikeButton activityId={activity.id} />
        </div>

        {/* Métricas — 5 colunas no md+ (distância, duração, pace, elevação, calorias) */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
          <Metric label="Distância" value={formatDistance(activity.distance_m)} />
          <Metric label="Duração" value={formatDuration(activity.duration_s)} />
          <Metric label="Pace médio" value={formatPace(activity.avg_pace_s_per_km)} />
          <Metric
            label="Elevação"
            value={
              activity.elevation_gain_m
                ? `${Math.round(activity.elevation_gain_m)} m`
                : "—"
            }
          />
          <Metric label="Calorias" value={formatCalories(activity.calories)} />
        </div>

        {/* Descrição */}
        {activity.description && (
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-1">
              Descrição
            </h2>
            <p className="text-gray-700 whitespace-pre-wrap">
              {activity.description}
            </p>
          </div>
        )}

        {/* Comentários */}
        <div className="mb-6">
          <CommentsSection activityId={activity.id} />
        </div>

        {/* Deletar — só o dono */}
        {isOwner && (
          <div className="pt-4 border-t border-gray-200">
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="text-sm text-red-600 hover:text-red-800 hover:underline disabled:opacity-50"
            >
              {deleteMutation.isPending ? "Apagando…" : "Apagar atividade"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white shadow-sm p-4">
      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
      <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
    </div>
  );
}