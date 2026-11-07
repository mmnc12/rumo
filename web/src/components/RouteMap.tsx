// [Sessão 13] Extraído do ActivityDetailPage. Encapsula o mapa da rota e o
// toggle Mapa/Satélite. Comportamento idêntico ao bloco inline anterior.
import { useEffect, useState } from "react";
import { MapContainer, Polyline, TileLayer, useMap } from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";

import type { TrackResponse } from "../types/api";

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

interface RouteMapProps {
  /** Geometria da rota (de useActivityTrack). `undefined` = ainda carregando
   *  ou atividade sem rota; nesses casos o componente exibe o estado vazio. */
  track: TrackResponse | undefined;
  /** Altura do mapa. Default "24rem" (mesmo valor que o detalhe usava). */
  height?: string;
  /** Classe extra no wrapper (ex.: margem). Default vazio. */
  className?: string;
}

/**
 * Mapa da rota de uma atividade, com toggle Mapa/Satélite.
 *
 * Encapsula: TileLayer OSM ↔ Esri, Polyline das coordenadas, fit bounds
 * ao bbox, e o botão de alternância no canto superior direito.
 */
export function RouteMap({
  track,
  height = "24rem",
  className = "",
}: RouteMapProps) {
  // [Sessão 11 — fix] Camada ativa: false = mapa (OSM), true = satélite (Esri).
  const [satelite, setSatelite] = useState(false);

  // Inverte [lon, lat] (GeoJSON) → [lat, lng] (Leaflet)
  const positions =
    track?.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]) ?? [];

  if (positions.length === 0 || !track) {
    return (
      <div
        className={`rounded-lg bg-gray-100 flex items-center justify-center ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500">Sem rota disponível pra esta atividade.</p>
      </div>
    );
  }

  return (
    <div
      className={`relative rounded-lg overflow-hidden shadow-sm ${className}`}
      style={{ height }}
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
  );
}