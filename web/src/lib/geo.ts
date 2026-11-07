// [Sessão 11] Conversões geo para miniatura estática de mapa (OSM tiles).
// [Sessão 16] Adicionado mosaico 2×2 (bboxToOsmTileGrid) para o feed.
// [Sessão 17] Removido bboxToOsmTileUrl (deprecated na S16, sem uso desde
//             então). bboxToOsmTileGrid passou a ser a única conversão geo
//             deste módulo.

// [Sessão 16] Mosaico 2×2 de tiles OSM para miniatura do feed.

export interface OsmTile {
  /** URL do tile individual. */
  url: string;
  /** Posição do tile no mosaico 2×2 (linha 0 = norte, coluna 0 = oeste). */
  row: 0 | 1;
  col: 0 | 1;
}

export interface OsmTileGrid {
  /** 4 tiles na ordem [NW, NE, SW, SE] — prontos para um `grid-cols-2`. */
  tiles: OsmTile[];
  /** Zoom usado (informativo; hoje fixo em 13). */
  zoom: number;
  /** Centro do bbox em [lat, lon] (informativo / debug). */
  center: [number, number];
}

/**
 * Converte um bbox GeoJSON `[minLon, minLat, maxLon, maxLat]` em um mosaico
 * 2×2 de tiles OSM estáticos.
 *
 * Motivação: um tile único cobre só ~1 tile de área — rotas com bbox maior
 * cortam as bordas no thumbnail. O mosaico 2×2 cobre 2× a largura e 2× a
 * altura, alinhado com o bbox, sem dependência nova (nada de react-leaflet,
 * nada de serviço externo tipo staticmap).
 *
 * Algoritmo:
 *  1. Calcula o centro (lat, lon) do bbox.
 *  2. Converte (lat, lon, zoom) → (x, y) tile (slippy map / EPSG:3857).
 *  3. Retorna os 4 tiles vizinhos: (x,y), (x+1,y), (x,y+1), (x+1,y+1),
 *     na ordem [NW, NE, SW, SE].
 *
 * Zoom default é 13 porque o mosaico já dobra a área coberta — subir o zoom
 * mantém o nível de detalhe e ainda amplia a cobertura útil.
 */
export function bboxToOsmTileGrid(
  bbox: [number, number, number, number],
  zoom: number = 13
): OsmTileGrid {
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

  const makeTile = (tx: number, ty: number, row: 0 | 1, col: 0 | 1): OsmTile => ({
    url: `https://tile.openstreetmap.org/${zoom}/${tx}/${ty}.png`,
    row,
    col,
  });

  return {
    tiles: [
      makeTile(x, y, 0, 0), // NW
      makeTile(x + 1, y, 0, 1), // NE
      makeTile(x, y + 1, 1, 0), // SW
      makeTile(x + 1, y + 1, 1, 1), // SE
    ],
    zoom,
    center: [lat, lon],
  };
}