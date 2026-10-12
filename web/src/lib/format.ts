/**
 * Formatadores de exibição do Rumo.
 *
 * Tudo aqui é puro (sem React) — facilita testar e reusar no mobile.
 * Padrão brasileiro: vírgula decimal, "5,2 km", "6:00 /km".
 */

/**
 * Distância: metros → "5,2 km" | "850 m"
 * Abaixo de 1km mostra em metros (mais legível pra caminhada curta).
 */
export function formatDistance(meters: number | null | undefined): string {
  if (meters == null) return "—";
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }
  const km = meters / 1000;
  return `${km.toFixed(2).replace(".", ",")} km`;
}

/**
 * Duração: segundos → "1h 05min" | "32min" | "45s"
 * Não usa Date porque não é uma data, é uma quantidade de tempo.
 */
export function formatDuration(seconds: number | null | undefined): string {
  if (seconds == null) return "—";
  const s = Math.round(seconds);
  if (s < 60) return `${s}s`;

  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const rem = s % 60;

  if (h > 0) {
    // 1h 05min — sempre 2 dígitos nos minutos pra alinhar
    return `${h}h ${String(m).padStart(2, "0")}min`;
  }
  if (m > 0 && rem > 0 && m < 10) {
    // 5min 30s — mostra segundos só em durações curtas
    return `${m}min ${rem}s`;
  }
  return `${m}min`;
}

/**
 * Pace: segundos por km → "5:30 /km"
 * O Strava mostra pace como mm:ss por km. Esse é o formato canônico.
 * Se null (ex: ciclismo não tem pace), retorna "—".
 */
export function formatPace(sPerKm: number | null | undefined): string {
  if (sPerKm == null) return "—";
  const total = Math.round(sPerKm);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")} /km`;
}

/**
 * Velocidade: m/s → "12,4 km/h"
 * Usado pra ciclismo (pace por km não faz sentido quando se anda a 30km/h).
 */
export function formatSpeed(mps: number | null | undefined): string {
  if (mps == null) return "—";
  const kmh = mps * 3.6;
  return `${kmh.toFixed(1).replace(".", ",")} km/h`;
}

/**
 * Data absoluta: "12 out 2026, 15:30"
 * Intl.DateTimeFormat com pt-BR.
 */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}

/**
 * Data relativa: "há 2 horas", "ontem", "há 3 dias"
 * Cálculo manual — Intl.RelativeTimeFormat é verboso e não dá exatamente
 * o "há X" que a gente quer em pt-BR.
 */
export function formatRelativeDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const then = new Date(iso).getTime();
  const now = Date.now();
  const diffSec = Math.floor((now - then) / 1000);

  if (diffSec < 60) return "agora há pouco";
  if (diffSec < 3600) {
    const m = Math.floor(diffSec / 60);
    return `há ${m} min`;
  }
  if (diffSec < 86400) {
    const h = Math.floor(diffSec / 3600);
    return `há ${h}h`;
  }
  if (diffSec < 172800) return "ontem";
  if (diffSec < 2592000) {
    const d = Math.floor(diffSec / 86400);
    return `há ${d} dias`;
  }
  // Mais de 30 dias — cai pra data absoluta
  return formatDateTime(iso);
}

/**
 * Nome amigável do tipo de atividade.
 */
export function formatActivityType(type: string): string {
  const map: Record<string, string> = {
    run: "Corrida",
    walk: "Caminhada",
    cycle: "Ciclismo",
    hike: "Trilha",
    swim: "Natação",
    other: "Outro",
  };
  return map[type] ?? type;
}

/**
 * Emoji do tipo — usado nos cards pra dar identidade visual sem imagem.
 */
export function activityEmoji(type: string): string {
  const map: Record<string, string> = {
    run: "🏃",
    walk: "🚶",
    cycle: "🚴",
    hike: "🥾",
    swim: "🏊",
    other: "💪",
  };
  return map[type] ?? "💪";
}