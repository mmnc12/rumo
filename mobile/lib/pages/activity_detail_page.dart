import 'dart:convert';

import 'package:flutter/material.dart';

import '../models/activity.dart';
import '../models/comment.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../widgets/like_button.dart';

class ActivityDetailPage extends StatefulWidget {
  final String activityId;
  final AuthService auth;

  const ActivityDetailPage({
    super.key,
    required this.activityId,
    required this.auth,
  });

  @override
  State<ActivityDetailPage> createState() => _ActivityDetailPageState();
}

class _ActivityDetailPageState extends State<ActivityDetailPage> {
  Activity? _activity;
  bool _loading = true;
  String? _error;

  // Comentários
  List<Comment> _comments = const [];
  bool _commentsLoading = false;
  String? _commentsError;
  final TextEditingController _commentController = TextEditingController();
  bool _sendingComment = false;

  @override
  void initState() {
    super.initState();
    _load();
    _loadComments();
  }

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await widget.auth.api.get(
        '/activities/${widget.activityId}',
        token: widget.auth.token,
      );
      setState(() {
        _activity = Activity.fromJson(data as Map<String, dynamic>);
      });
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Erro: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _loadComments() async {
    setState(() {
      _commentsLoading = true;
      _commentsError = null;
    });

    try {
      final comments = await widget.auth.api.listComments(
        widget.activityId,
        token: widget.auth.token,
      );
      setState(() => _comments = comments);
    } on ApiException catch (e) {
      setState(() => _commentsError = e.message);
    } catch (e) {
      setState(() => _commentsError = 'Erro: $e');
    } finally {
      setState(() => _commentsLoading = false);
    }
  }

  /// Atualiza o estado local quando a curtida muda (otimista ou rollback).
  void _onLikeChanged(Activity updated) {
    setState(() {
      _activity = updated;
    });
  }

  /// Extrai o id do usuário atual a partir do JWT (`sub`), sem depender
  /// de um getter específico do AuthService.
  String? get _currentUserId {
    final token = widget.auth.token;
    if (token == null) return null;
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;
      final payload = parts[1];
      final normalized = base64Url.normalize(payload);
      final decoded = utf8.decode(base64Url.decode(normalized));
      final data = jsonDecode(decoded);
      if (data is Map<String, dynamic>) {
        final sub = data['sub'];
        if (sub is String) return sub;
        final userId = data['user_id'];
        if (userId is String) return userId;
      }
    } catch (_) {
      // token inválido/expirado — sem id, esconde o botão de deletar.
    }
    return null;
  }

  Future<void> _submitComment() async {
    final text = _commentController.text.trim();
    if (text.isEmpty || _sendingComment) return;

    setState(() => _sendingComment = true);
    try {
      final created = await widget.auth.api.createComment(
        widget.activityId,
        text,
        token: widget.auth.token,
      );
      setState(() {
        _comments = [..._comments, created];
        _commentController.clear();
        // Atualiza o contador localmente sem recarregar a atividade.
        _activity = _activity?.copyWith(
          commentsCount: _comments.length,
        );
      });
    } on ApiException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('Erro: $e');
    } finally {
      if (mounted) setState(() => _sendingComment = false);
    }
  }

  Future<void> _deleteComment(Comment comment) async {
    try {
      await widget.auth.api.deleteComment(
        comment.id,
        token: widget.auth.token,
      );
      setState(() {
        _comments = _comments.where((c) => c.id != comment.id).toList();
        _activity = _activity?.copyWith(
          commentsCount: _comments.length,
        );
      });
    } on ApiException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('Erro: $e');
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Detalhe')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _load,
                        child: const Text('Tentar novamente'),
                      ),
                    ],
                  ),
                )
              : _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    final a = _activity!;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          a.title ?? a.typeLabel,
          style: theme.textTheme.headlineSmall,
        ),
        const SizedBox(height: 4),
        Text(
          '${a.typeLabel} • ${a.startedAtLabel}',
          style: theme.textTheme.bodySmall,
        ),

        // Autor e Botão de Curtir
        if (a.user != null) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              CircleAvatar(
                radius: 20,
                backgroundImage: a.user!.avatarUrl != null
                    ? NetworkImage(a.user!.avatarUrl!)
                    : null,
                child: a.user!.avatarUrl == null
                    ? Text(a.user!.username.substring(0, 1).toUpperCase())
                    : null,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  a.user!.fullName ?? a.user!.username,
                  style: theme.textTheme.titleMedium,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              // Botão de curtir integrado
              LikeButton(
                activity: a,
                auth: widget.auth,
                onChanged: _onLikeChanged,
              ),
            ],
          ),
        ],

        const SizedBox(height: 24),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 2.2,
          children: [
            if (a.distanceLabel != null)
              _StatCard(label: 'Distância', value: a.distanceLabel!, icon: Icons.straighten),
            if (a.durationLabel != null)
              _StatCard(label: 'Duração', value: a.durationLabel!, icon: Icons.timer_outlined),
            if (a.paceLabel != null)
              _StatCard(label: 'Ritmo', value: a.paceLabel!, icon: Icons.speed),
            if (a.caloriesLabel != null)
              _StatCard(label: 'Calorias', value: a.caloriesLabel!, icon: Icons.local_fire_department),
            if (a.elevationGainM != null)
              _StatCard(
                label: 'Elevação',
                value: '${a.elevationGainM!.round()} m',
                icon: Icons.terrain,
              ),
            if (a.avgSpeedMps != null)
              _StatCard(
                label: 'Vel. média',
                value: '${(a.avgSpeedMps! * 3.6).toStringAsFixed(1)} km/h',
                icon: Icons.speed,
              ),
          ],
        ),
        if (a.description != null && a.description!.isNotEmpty) ...[
          const SizedBox(height: 24),
          Text('Descrição', style: theme.textTheme.titleMedium),
          const SizedBox(height: 8),
          Text(a.description!),
        ],

        // ---------- Comentários ----------
        const SizedBox(height: 24),
        Row(
          children: [
            Icon(Icons.chat_bubble_outline,
                size: 18, color: theme.colorScheme.primary),
            const SizedBox(width: 6),
            Text(
              'Comentários (${a.commentsCount})',
              style: theme.textTheme.titleMedium,
            ),
          ],
        ),
        const SizedBox(height: 12),
        _buildCommentsSection(theme),
      ],
    );
  }

  Widget _buildCommentsSection(ThemeData theme) {
    if (_commentsLoading) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 16),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (_commentsError != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(_commentsError!, style: theme.textTheme.bodySmall),
          const SizedBox(height: 8),
          TextButton(
            onPressed: _loadComments,
            child: const Text('Tentar novamente'),
          ),
        ],
      );
    }

    final currentUserId = _currentUserId;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (_comments.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Text(
              'Nenhum comentário ainda. Seja o primeiro!',
              style: theme.textTheme.bodySmall,
            ),
          )
        else
          ..._comments.map(
            (c) => _CommentTile(
              comment: c,
              canDelete: c.canDelete(currentUserId),
              onDelete: () => _deleteComment(c),
            ),
          ),
        const SizedBox(height: 12),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: TextField(
                controller: _commentController,
                minLines: 1,
                maxLines: 4,
                maxLength: 500,
                decoration: const InputDecoration(
                  hintText: 'Escreva um comentário…',
                  border: OutlineInputBorder(),
                  isDense: true,
                  counterText: '',
                ),
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _submitComment(),
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: _sendingComment ? null : _submitComment,
              icon: _sendingComment
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send),
              tooltip: 'Enviar',
            ),
          ],
        ),
      ],
    );
  }
}

class _CommentTile extends StatelessWidget {
  final Comment comment;
  final bool canDelete;
  final VoidCallback onDelete;

  const _CommentTile({
    required this.comment,
    required this.canDelete,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final author = comment.author;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 16,
            backgroundImage: author?.avatarUrl != null
                ? NetworkImage(author!.avatarUrl!)
                : null,
            child: author?.avatarUrl == null
                ? Text(
                    (author?.username.isNotEmpty ?? false)
                        ? author!.username.substring(0, 1).toUpperCase()
                        : '?',
                    style: theme.textTheme.labelSmall,
                  )
                : null,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  author?.fullName ?? author?.username ?? 'Usuário',
                  style: theme.textTheme.labelLarge,
                ),
                const SizedBox(height: 2),
                Text(comment.content, style: theme.textTheme.bodyMedium),
              ],
            ),
          ),
          if (canDelete)
            IconButton(
              onPressed: onDelete,
              icon: const Icon(Icons.delete_outline, size: 18),
              tooltip: 'Excluir comentário',
            ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Icon(icon, size: 16, color: theme.colorScheme.primary),
                const SizedBox(width: 4),
                Text(label, style: theme.textTheme.labelSmall),
              ],
            ),
            const SizedBox(height: 4),
            Text(value, style: theme.textTheme.titleMedium),
          ],
        ),
      ),
    );
  }
}