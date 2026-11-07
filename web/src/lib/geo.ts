// [Sessão 11] Conversões geo para miniatura estática de mapa (OSM tiles).

/**
 * Converte um bbox GeoJSON `[minLon, minLat, maxLon, maxLat]` em uma URL de
 * tile estático do OpenStreetMap que enquadra o centro do bbox.
 *
 * Usa 1 único tile (não mosaico): suficiente para miniatura. Rotas muito
 * espalhadas podem cortar as bordas do bbox — aceitável para thumbnail.
 *
 * Algoritmo (slippy map / EPSG:3857):
 *  1. Calcula o centro (lat, lon) do bbox.
 *  2. Escolhe zoom ~12 fixo como default (ajustável via `zoom`).
 *  3. Converte (lat, lon, zoom) → (x, y) tile.
 *  4. Monta URL https://tile.openstreetmap.org/{z}/{x}/{y}.png
 */
export function bboxToOsmTileUrl(
  bbox: [number, number, number, number],
  zoom: number = 12
): string {
  const [minLon, minLat, maxLon, maxLat] = bbox;

  // Centro do bbox.
  const lat = (minLat + maxLat) / 2;
  const lon = (minLon + maxLon) / 2;

  // Slippy map math (EPSG:3857).
  const n = 2 ** zoom;
  const x = Math.floor(((lon + 180) / 360) * n);
  const latRad = (lat * Math.PI) / 180;
  const y = Math.floor(
    ((1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2) * n
  );

  return `https://tile.openstreetmap.org/${zoom}/${x}/${y}.png`;
}