import 'package:flutter/material.dart';

import '../models/activity.dart';
import '../models/activity_track.dart';
import '../models/comment.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../utils/download.dart'; // [Sessão 37] saveAndShare
import '../widgets/activity_map.dart';
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

// [Sessão 37] Formatos de export suportados pelo backend (S21).
enum _ExportFormat { csv, gpx }

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

  // Rota (mapa)
  ActivityTrack? _track;
  bool _trackLoading = false;
  String? _trackError;

  // [Sessão 37] Estado do menu de export (CSV/GPX).
  bool _exporting = false;

  @override
  void initState() {
    super.initState();
    _load();
    _loadComments();
    _loadTrack();
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

  Future<void> _loadTrack() async {
    setState(() {
      _trackLoading = true;
      _trackError = null;
    });

    try {
      final track = await widget.auth.api.getActivityTrack(
        widget.activityId,
        token: widget.auth.token,
      );
      // `null` = 404 do backend (atividade sem rota). Esconde o card.
      setState(() => _track = track);
    } on ApiException catch (e) {
      setState(() => _trackError = e.message);
    } catch (e) {
      setState(() => _trackError = 'Erro: $e');
    } finally {
      setState(() => _trackLoading = false);
    }
  }

  /// [Sessão 37] Export CSV/GPX da atividade atual.
  Future<void> _export(_ExportFormat format) async {
    if (_exporting) return;
    setState(() => _exporting = true);
    try {
      final result = await widget.auth.api.downloadActivityExport(
        activityId: widget.activityId,
        format: format.name,
        token: widget.auth.token,
      );
      await saveAndShare(
        bytes: result.bytes,
        filename: result.filename,
        contentType: result.contentType,
        shareText: format == _ExportFormat.csv
            ? 'Exportação CSV da atividade — Rumo'
            : 'Exportação GPX da atividade — Rumo',
      );
    } on ApiException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('Erro ao exportar: $e');
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  /// Atualiza o estado local quando a curtida muda (otimista ou rollback).
  void _onLikeChanged(Activity updated) {
    setState(() {
      _activity = updated;
    });
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
      appBar: AppBar(
        title: const Text('Detalhe'),
        actions: [
          if (_exporting)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Center(
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else
            PopupMenuButton<_ExportFormat>(
              icon: const Icon(Icons.ios_share),
              tooltip: 'Exportar',
              onSelected: _export,
              itemBuilder: (context) => const [
                PopupMenuItem(
                  value: _ExportFormat.csv,
                  child: ListTile(
                    leading: Icon(Icons.table_chart_outlined),
                    title: Text('Exportar CSV'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
                PopupMenuItem(
                  value: _ExportFormat.gpx,
                  child: ListTile(
                    leading: Icon(Icons.route),
                    title: Text('Exportar GPX'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
              ],
            ),
        ],
      ),
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
    
    // [Sessão 46] Correção do BOTTOM OVERFLOWED:
    // Trocado GridView.count (que exige childAspectRatio fixo) por Wrap.
    // O Wrap mede a altura real de cada card e quebra a linha sem vazar.
    final stats = <Widget>[
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
    ];

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
              LikeButton(
                activity: a,
                auth: widget.auth,
                onChanged: _onLikeChanged,
              ),
            ],
          ),
        ],

        const SizedBox(height: 24),
        
        // [Sessão 46] Wrap em vez de GridView
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: stats,
        ),

        // ---------- Rota (mapa) ----------
        ..._buildTrackSection(theme),

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

  /// Card "Rota". Regras:
  /// - `_trackLoading` → spinner.
  /// - `_trackError`   → mensagem + retry.
  /// - `_track == null` (404, sem rota) → não renderiza nada.
  /// - `_track != null` → mapa.
  List<Widget> _buildTrackSection(ThemeData theme) {
    if (_trackLoading) {
      return [
        const SizedBox(height: 24),
        Row(
          children: [
            Icon(Icons.route, size: 18, color: theme.colorScheme.primary),
            const SizedBox(width: 6),
            Text('Rota', style: theme.textTheme.titleMedium),
          ],
        ),
        const SizedBox(height: 12),
        const SizedBox(
          height: 120,
          child: Center(child: CircularProgressIndicator()),
        ),
      ];
    }

    if (_trackError != null) {
      return [
        const SizedBox(height: 24),
        Row(
          children: [
            Icon(Icons.route, size: 18, color: theme.colorScheme.primary),
            const SizedBox(width: 6),
            Text('Rota', style: theme.textTheme.titleMedium),
          ],
        ),
        const SizedBox(height: 8),
        Text(_trackError!, style: theme.textTheme.bodySmall),
        TextButton(
          onPressed: _loadTrack,
          child: const Text('Tentar novamente'),
        ),
      ];
    }

    final track = _track;
    if (track == null) {
      // 404: atividade não tem rota — esconde a seção inteira.
      return const [];
    }

    return [
      const SizedBox(height: 24),
      Row(
        children: [
          Icon(Icons.route, size: 18, color: theme.colorScheme.primary),
          const SizedBox(width: 6),
          Text('Rota', style: theme.textTheme.titleMedium),
          const Spacer(),
          Text(
            '${track.nPoints} pts',
            style: theme.textTheme.labelSmall,
          ),
        ],
      ),
      const SizedBox(height: 12),
      // [Sessão 46] O mapa estava gerando overflow lateral por causa dos
      // créditos do flutter_map. Envolvemos em ClipRRect + SizedBox para
      // conter o widget e evitar o vazamento.
      ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: SizedBox(
          width: double.infinity,
          height: 280, // Altura fixa para o mapa, evita conflito com ListView
          child: ActivityMap(track: track),
        ),
      ),
    ];
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

    // [Sessão 10] Id do usuário agora vem do AuthService (fonte única).
    final currentUserId = widget.auth.currentUserId;

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
    
    // [Sessão 46] O Card agora tem largura definida para funcionar bem no Wrap
    // e o conteúdo interno se ajusta automaticamente.
    return Container(
      width: 160, // Largura fixa para alinhar os cards em 2 colunas
      constraints: const BoxConstraints(minHeight: 70), // Altura mínima
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min, // Ocupa apenas o espaço necessário
          children: [
            Row(
              children: [
                Icon(icon, size: 16, color: theme.colorScheme.primary),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    label,
                    style: theme.textTheme.labelSmall,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: theme.textTheme.titleMedium,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}