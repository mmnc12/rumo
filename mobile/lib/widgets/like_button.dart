import 'package:flutter/material.dart';

import '../models/activity.dart';
import '../services/api.dart';
import '../services/auth_service.dart';

/// Botão de curtir com estado otimista.
///
/// - Exibe coração cheio/vazio conforme `activity.likedByMe`.
/// - Exibe contador (`activity.likesCount`).
/// - Ao tocar: atualiza UI imediatamente, chama `POST` ou `DELETE`
///   `/activities/{id}/like`, e em erro faz rollback + SnackBar.
///
/// O widget é "stateless do ponto de vista do pai": recebe o `Activity`
/// atual e um `onChanged` que o pai usa para substituir o item na lista.
class LikeButton extends StatefulWidget {
  final Activity activity;
  final AuthService auth;
  final ValueChanged<Activity> onChanged;

  const LikeButton({
    super.key,
    required this.activity,
    required this.auth,
    required this.onChanged,
  });

  @override
  State<LikeButton> createState() => _LikeButtonState();
}

class _LikeButtonState extends State<LikeButton> {
  bool _inFlight = false;

  Future<void> _toggle() async {
    if (_inFlight) return;

    final current = widget.activity;
    final willLike = !current.likedByMe;

    // Estado otimista
    final optimistic = current.copyWith(
      likedByMe: willLike,
      likesCount: (current.likesCount + (willLike ? 1 : -1)).clamp(0, 1 << 31),
    );
    widget.onChanged(optimistic);

    setState(() => _inFlight = true);
    try {
      if (willLike) {
        await widget.auth.api.post(
          '/activities/${current.id}/like',
          token: widget.auth.token,
        );
      } else {
        await widget.auth.api.delete(
          '/activities/${current.id}/like',
          token: widget.auth.token,
        );
      }
    } on ApiException catch (e) {
      // rollback
      widget.onChanged(current);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Não foi possível curtir: ${e.message}')),
        );
      }
    } catch (e) {
      widget.onChanged(current);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _inFlight = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final liked = widget.activity.likedByMe;
    final theme = Theme.of(context);
    final color = liked ? Colors.red : theme.colorScheme.onSurfaceVariant;

    return InkWell(
      onTap: _toggle,
      borderRadius: BorderRadius.circular(20),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              liked ? Icons.favorite : Icons.favorite_border,
              size: 20,
              color: color,
            ),
            const SizedBox(width: 4),
            Text(
              '${widget.activity.likesCount}',
              style: theme.textTheme.bodySmall?.copyWith(color: color),
            ),
          ],
        ),
      ),
    );
  }
}