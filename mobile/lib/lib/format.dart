// [Sessão 33] Formatadores de exibição do Rumo (mobile).
//
// Portado de web/src/lib/format.ts — só as funções que a S33 usa:
// - formatDistance: metros → "850 m" | "5,20 km"
// - formatElevation: metros → "850 m" | "1.234 m" (sempre metros, milhar pt-BR)
// - formatDuration: segundos → "45s" | "32min" | "5min 30s" | "1h 05min"
// - formatCalories: kcal → "248 kcal" | "1.234 kcal" (milhar pt-BR)
// - formatPace: s/km → "5:30 /km"
// - computePace: (total_duration_s, total_distance_m) → s/km | null
//
// Padrão brasileiro: vírgula decimal, "5,20 km", "6:00 /km".
// Tudo puro (sem Flutter) — facilita testar e reusar.
//
// NÃO portados (YAGNI — entram quando precisar):
// formatSpeed, formatDateTime, formatRelativeDate, formatActivityType, activityEmoji.

/// Distância: metros → "5,20 km" | "850 m"
///
/// Abaixo de 1 km mostra em metros (mais legível pra caminhada curta).
/// Retorna "—" quando null.
String formatDistance(num? meters) {
  if (meters == null) return '—';
  final m = meters.toDouble();
  if (m < 1000) {
    return '${m.round()} m';
  }
  final km = m / 1000;
  // toFixed(2) com vírgula pt-BR.
  return '${km.toStringAsFixed(2).replaceAll('.', ',')} km';
}

/// Elevação: metros → "850 m" | "1.234 m"
///
/// Diferente de formatDistance: elevação NUNCA vira km, mesmo em
/// montanhas de 2000 m — o padrão de mercado (Strava, Garmin) é sempre
/// metros. Usa separador de milhar pt-BR pra deixar "1.234 m" legível
/// sem perder precisão inteira.
///
/// Retorna "—" quando null (upload sem dados de altitude).
String formatElevation(num? meters) {
  if (meters == null) return '—';
  final m = meters.round();
  return '${_formatThousands(m)} m';
}

/// Duração: segundos → "1h 05min" | "32min" | "45s"
///
/// Não usa DateTime porque não é uma data, é uma quantidade de tempo.
/// Retorna "—" quando null.
String formatDuration(num? seconds) {
  if (seconds == null) return '—';
  final s = seconds.round();
  if (s < 60) return '${s}s';

  final h = s ~/ 3600;
  final m = (s % 3600) ~/ 60;
  final rem = s % 60;

  if (h > 0) {
    // 1h 05min — sempre 2 dígitos nos minutos pra alinhar.
    return '${h}h ${m.toString().padLeft(2, '0')}min';
  }
  if (m > 0 && rem > 0 && m < 10) {
    // 5min 30s — mostra segundos só em durações curtas.
    return '${m}min ${rem}s';
  }
  return '${m}min';
}

/// Calorias: kcal → "248 kcal" | "1.234 kcal"
///
/// Formata com separador de milhar pt-BR. Sem decimal — kcal é estimativa,
/// precisão ao nível da unidade não agrega e polui.
/// Retorna "—" quando null.
String formatCalories(num? kcal) {
  if (kcal == null) return '—';
  final k = kcal.round();
  return '${_formatThousands(k)} kcal';
}

/// Pace: segundos por km → "5:30 /km"
///
/// O Strava mostra pace como mm:ss por km. Esse é o formato canônico.
/// Retorna "—" quando null.
String formatPace(num? sPerKm) {
  if (sPerKm == null) return '—';
  final total = sPerKm.round();
  final m = total ~/ 60;
  final s = total % 60;
  return '$m:${s.toString().padLeft(2, '0')} /km';
}

/// Pace médio a partir dos totais (duração, distância).
///
/// Retorna `null` quando `totalDistanceM <= 0` (evita divisão por zero).
/// Mesma fórmula do `computePace` do web.
double? computePace({
  required num totalDurationS,
  required num totalDistanceM,
}) {
  if (totalDistanceM <= 0) return null;
  return totalDurationS / (totalDistanceM / 1000);
}

// ---------- internos ----------

/// Formata inteiro com separador de milhar pt-BR ("1234" → "1.234").
///
/// `intl` não está no pubspec do mobile hoje; fazer inline com 3 dígitos
/// é trivial e evita dependência nova só pra isso.
String _formatThousands(int n) {
  final negative = n < 0;
  final digits = n.abs().toString();
  final buf = StringBuffer();
  for (var i = 0; i < digits.length; i++) {
    final remaining = digits.length - i;
    if (i > 0 && remaining % 3 == 0) {
      buf.write('.');
    }
    buf.write(digits[i]);
  }
  return negative ? '-$buf' : buf.toString();
}