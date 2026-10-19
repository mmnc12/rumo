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
  /** URL Cloudinary da primeira foto (denormalizado, bloco 17b backend). */
  cover_photo_url: string | null;
  /** Quantidade total de fotos (denormalizado, bloco 17b backend). */
  photo_count: number;
}

/**
 * Detalhe de uma atividade, com autor aninhado.
 *
 * Só o GET /activities/{id} retorna este shape — listagem e feed usam
 * Activity (sem author) e FeedItem (com author) respectivamente.
 */
export interface ActivityDetail extends Activity {
  author: UserPublic;
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

// ===== Stats (16) =====

/** Totais gerais do usuário (com filtro opcional por tipo). */
export interface StatsSummary {
  total_activities: number;
  total_distance_m: number;
  total_duration_s: number;
  total_elevation_gain_m: number;
  total_calories: number;
  avg_pace_s_per_km: number | null;
  avg_speed_mps: number | null;
}

/** Resumo de um período (semana ou mês). */
export interface StatsPeriod {
  period_start: string; // ISO date "YYYY-MM-DD"
  total_activities: number;
  total_distance_m: number;
  total_duration_s: number;
  total_calories: number;
}

/** Lista de resumos semanais. */
export interface StatsWeeklyResponse {
  weeks: number;
  items: StatsPeriod[];
}

/** Lista de resumos mensais. */
export interface StatsMonthlyResponse {
  months: number;
  items: StatsPeriod[];
}

export interface ActivityPhoto {
  id: string;
  activity_id: string;
  url: string;
  width: number | null;
  height: number | null;
  created_at: string;
}

// ===== Notificações (17) =====

export type NotificationType = "like" | "comment" | "follow";

/** Preview da atividade aninhado na notificação (evita carregar a atividade inteira). */
export interface NotificationActivityPreview {
  id: string;
  title: string | null;
  activity_type: ActivityType;
}

export interface Notification {
  id: string;
  type: NotificationType;
  is_read: boolean;
  created_at: string;
  actor: UserPublic;
  activity: NotificationActivityPreview | null;
  comment_id: string | null;
}

export interface UnreadCountResponse {
  count: number;
}

export interface MarkAllReadResponse {
  updated: number;
}