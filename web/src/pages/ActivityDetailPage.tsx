// [Sessão 11 — fix] toggle Mapa/Satélite no mapa do detalhe (igual mobile).
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { MapContainer, Polyline, TileLayer, useMap } from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";

import { AppHeader } from "../components/AppHeader";
import { CommentsSection } from "../components/CommentsSection";
import { LikeButton } from "../components/LikeButton";
import { PhotoGallery } from "../components/PhotoGallery";
import { PhotoUpload } from "../components/PhotoUpload";
import { useAuth } from "../hooks/useAuth";
import {
  useActivity,
  useActivityTrack,
  useDeleteActivity,
} from "../hooks/useActivities";
import { useActivityPhotos, useDeletePhoto } from "../hooks/usePhotos";
import {
  activityEmoji,
  formatActivityType,
  formatCalories,
  formatDateTime,
  formatDistance,
  formatDuration,
  formatPace,
} from "../lib/format";

// [Sessão 11 — fix] Providers alinhados com o mobile (ActivityMap).
// Ordem dos placeholders difere:
//   OSM:   {z}/{x}/{y}
//   Esri:  {z}/{y}/{x}
const OSM_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const OSM_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
const ESRI_URL =
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const ESRI_ATTRIBUTION =
  "Esri, Maxar, Earthstar Geographics, and the GIS User Community";

/** Ajusta o zoom do mapa pra enquadrar a rota inteira. */
function FitBounds({ bbox }: { bbox: [number, number, number, number] }) {
  const map = useMap();
  useEffect(() => {
    // bbox vem [minLon, minLat, maxLon, maxLat] do backend.
    // Leaflet espera [[lat, lng], [lat, lng]] → [[minLat, minLon], [maxLat, maxLon]]
    const bounds: LatLngBoundsExpression = [
      [bbox[1], bbox[0]],
      [bbox[3], bbox[2]],
    ];
    map.fitBounds(bounds, { padding: [24, 24] });
  }, [bbox, map]);
  return null;
}

export default function ActivityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const { data: activity, isLoading, error } = useActivity(id);
  const { data: track } = useActivityTrack(id);
  const { data: photos } = useActivityPhotos(id);
  const deleteMutation = useDeleteActivity();
  const deletePhoto = useDeletePhoto(id ?? "");

  // [Sessão 11 — fix] Camada ativa: false = mapa (OSM), true = satélite (Esri).
  const [satelite, setSatelite] = useState(false);

  async function handleDelete() {
    if (!id) return;
    if (!confirm("Tem certeza que quer apagar esta atividade?")) return;
    await deleteMutation.mutateAsync(id);
    navigate("/activities");
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

  // Inverte [lon, lat] (GeoJSON) → [lat, lng] (Leaflet)
  const positions =
    track?.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]) ?? [];

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

          <h1 className="text-2xl font-bold flex items-center gap-2">
            <span>{activityEmoji(activity.activity_type)}</span>
            <span>
              {activity.title || formatActivityType(activity.activity_type)}
            </span>
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {formatDateTime(activity.started_at)}
          </p>
        </div>

        {/* Mapa */}
        {positions.length > 0 && track ? (
          <div
            className="relative rounded-lg overflow-hidden shadow-sm mb-6"
            style={{ height: "24rem" }}
          >
            <MapContainer
              style={{ height: "100%", width: "100%" }}
              center={[positions[0][0], positions[0][1]]}
              zoom={13}
              scrollWheelZoom
            >
              {/* [Sessão 11 — fix] `key` força remount do TileLayer ao trocar
                  de camada; sem isso o Leaflet mantém os tiles antigos em cache. */}
              <TileLayer
                key={satelite ? "esri" : "osm"}
                attribution={satelite ? ESRI_ATTRIBUTION : OSM_ATTRIBUTION}
                url={satelite ? ESRI_URL : OSM_URL}
              />
              <Polyline
                positions={positions}
                pathOptions={{ color: "#f97316", weight: 4 }}
              />
              <FitBounds bbox={track.bbox} />
            </MapContainer>

            {/* [Sessão 11 — fix] Toggle Mapa/Satélite (mesmo padrão do mobile).
                z-[1000] alinha com os controles nativos do Leaflet (zoom etc.). */}
            <button
              type="button"
              onClick={() => setSatelite((v) => !v)}
              aria-label={satelite ? "Ver mapa" : "Ver satélite"}
              title={satelite ? "Ver mapa" : "Ver satélite"}
              className="absolute top-2 right-2 z-[1000] flex h-9 w-9 items-center justify-center rounded-full bg-white shadow-md hover:bg-gray-50 transition"
            >
              {satelite ? (
                // Ícone "mapa" (quadrado com linhas internas).
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5 text-gray-800"
                >
                  <path d="M9 4 3 6v16l6-2 6 2 6-2V4l-6 2-6-2z" />
                  <path d="M9 4v16" />
                  <path d="M15 6v16" />
                </svg>
              ) : (
                // Ícone "satélite" (antena + prato).
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5 text-gray-800"
                >
                  <path d="M13 7 9 3 5 7l4 4" />
                  <path d="m17 11 4 4-4 4-4-4" />
                  <path d="m8 12 4 4 6-6-4-4Z" />
                  <path d="m16 8 3-3" />
                  <path d="M9 21a6 6 0 0 0-6-6" />
                </svg>
              )}
            </button>
          </div>
        ) : (
          <div
            className="rounded-lg bg-gray-100 mb-6 flex items-center justify-center"
            style={{ height: "24rem" }}
          >
            <p className="text-gray-500">Sem rota disponível pra esta atividade.</p>
          </div>
        )}

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