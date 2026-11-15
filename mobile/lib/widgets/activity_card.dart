// [Sessão 32] Card de atividade extraído do feed_page.dart.
// Reutilizado pelo FeedPage e pelo ProfilePage ("minhas atividades").
// Comportamento idêntico ao _ActivityCard da Sessão 31 — só mudou de lugar
// e de nome (_ActivityCard → ActivityCard, público).
//
// [Sessão 33] +prop authorUsernameOverride. O GET /activities (usado pelo
// ProfilePage) NÃO embute `user`, só o GET /feed embute. Sem o override,
// o card no perfil cairia em "Usuário"/"?" — o ProfilePage passa
// _me.username e o card renderiza o username correto. O feed NÃO passa
// (continua usando activity.user). Resolve a dívida da S32 sem tocar
// backend. Quando o perfil de terceiro chegar (S34), o backend deve
// passar a embutir `user` no /activities e o override pode sair.
import 'package:flutter/material.dart';

import '../models/activity.dart';
import '../services/auth_service.dart';
import 'activity_map.dart';
import 'like_button.dart';

class ActivityCard extends StatelessWidget {
  final Activity activity;
  final AuthService auth;
  final VoidCallback onTap;
  final ValueChanged<Activity> onChanged;

  // [Sessão 33] Fallback de username quando `activity.user` é null.
  // Usado pelo ProfilePage (GET /activities não embute `user`).
  // O feed NÃO passa — lá o GET /feed já traz `user` embutido.
  final String? authorUsernameOverride;

  const ActivityCard({
    super.key,
    required this.activity,
    required this.auth,
    required this.onTap,
    required this.onChanged,
    this.authorUsernameOverride,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // [Sessão 33] Username: prioridade activity.user > override > "Usuário".
    // Avatar: activity.user?.avatarUrl (override não tem avatar — cai na inicial).
    final displayUsername =
        activity.user?.username ?? authorUsernameOverride ?? 'Usuário';
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Cabeçalho: avatar + username + tipo
              Row(
                children: [
                  CircleAvatar(
                    radius: 16,
                    backgroundImage: activity.user?.avatarUrl != null
                        ? NetworkImage(activity.user!.avatarUrl!)
                        : null,
                    child: activity.user?.avatarUrl == null
                        ? Text(
                            displayUsername.substring(0, 1).toUpperCase(),
                          )
                        : null,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      displayUsername,
                      style: theme.textTheme.titleSmall,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Text(
                    activity.typeLabel,
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Título
              Text(
                activity.title ?? activity.typeLabel,
                style: theme.textTheme.titleMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),

              // Miniatura de mapa (só se houver rota).
              if (activity.bbox != null) ...[
                const SizedBox(height: 8),
                // GestureDetector absorve o toque para abrir o detalhe,
                // já que o mapa em si está estático (InteractiveFlag.none).
                GestureDetector(
                  onTap: onTap,
                  child: ActivityMap.fromBbox(
                    bbox: activity.bbox!,
                    height: 120,
                  ),
                ),
              ],
              const SizedBox(height: 8),

              // Métricas
              Wrap(
                spacing: 12,
                runSpacing: 4,
                children: [
                  if (activity.distanceLabel != null)
                    ActivityCardMetric(
                      icon: Icons.straighten,
                      text: activity.distanceLabel!,
                    ),
                  if (activity.durationLabel != null)
                    ActivityCardMetric(
                      icon: Icons.timer_outlined,
                      text: activity.durationLabel!,
                    ),
                  if (activity.caloriesLabel != null)
                    ActivityCardMetric(
                      icon: Icons.local_fire_department,
                      text: activity.caloriesLabel!,
                    ),
                ],
              ),
              const SizedBox(height: 8),

              // Rodapé: data + curtidas + comentários
              Row(
                children: [
                  Expanded(
                    child: Text(
                      activity.startedAtLabel,
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                  LikeButton(
                    activity: activity,
                    auth: auth,
                    onChanged: onChanged,
                  ),
                  const SizedBox(width: 4),
                  // Botão de comentários com contador; navega para o detalhe.
                  TextButton.icon(
                    onPressed: onTap,
                    icon: const Icon(Icons.chat_bubble_outline, size: 18),
                    label: Text('${activity.commentsCount}'),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      minimumSize: const Size(0, 36),
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class ActivityCardMetric extends StatelessWidget {
  final IconData icon;
  final String text;
  const ActivityCardMetric({
    super.key,
    required this.icon,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16),
        const SizedBox(width: 4),
        Text(text),
      ],
    );
  }
}