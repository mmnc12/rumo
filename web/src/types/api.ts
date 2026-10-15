/**
 * Tipos espelhando os schemas Pydantic do backend.
 * Manter sincronizado manualmente por enquanto (Fase 2: gerar via OpenAPI).
 */

export type ActivityType = "run" | "walk" | "cycle" | "hike" | "swim" | "other";

export interface UserPublic {
  id: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
}

export interface UserResponse extends UserPublic {
  email: string;
  weight_kg: number | null;
  height_cm: number | null;
  birth_date: string | null;
  created_at: string;
}

export interface Activity {
  id: string;
  user_id: string;
  activity_type: ActivityType;
  title: string | null;
  description: string | null;
  started_at: string;
  finished_at: string | null;
  duration_s: number | null;
  distance_m: number;
  elevation_gain_m: number | null;
  calories: number | null;
  avg_pace_s_per_km: number | null;
  avg_speed_mps: number | null;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

/** Erro 422 do FastAPI (validação Pydantic). */
export interface ValidationErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

// ===== Track (geometria pro mapa) =====

export interface TrackResponse {
  activity_id: string;
  type: "LineString";
  /** [[lon, lat], ...] — ordem GeoJSON (lon primeiro!) */
  coordinates: [number, number][];
  /** [minLon, minLat, maxLon, maxLat] */
  bbox: [number, number, number, number];
  n_points: number;
  simplified: boolean;
}

// ===== Social (13b) =====

/** Atividade no feed, com dados do autor aninhados. */
export interface FeedItem extends Activity {
  author: UserPublic;
}

/** Estado de curtidas de uma atividade. */
export interface LikeState {
  count: number;
  liked_by_me: boolean;
}

/** Lista paginada de quem curtiu. */
export interface LikeList {
  count: number;
  liked_by_me: boolean;
  users: UserPublic[];
}

/** Comentário em uma atividade. */
export interface Comment {
  id: string;
  activity_id: string;
  content: string;
  created_at: string;
  updated_at: string;
  author: UserPublic;
}