// [Sessão 11] miniatura de mapa (bbox estático) no card do feed.
// [Sessão 31] FAB de upload de GPX/FIT.
// [Sessão 32] _ActivityCard extraído para widgets/activity_card.dart
//             (reuso no ProfilePage). Fix do setState() after dispose em
//             _load(). Logout movido para o ProfilePage (bottom nav).
// [Sessão 35] +IconButton(Icons.search) no AppBar → /search.
//             +onAuthorTap no ActivityCard: o avatar+username do card
//             abre o perfil do autor (antes herdava o onTap do card e
//             abria o detalhe). Fecha o ciclo "toca no autor → perfil"
//             que a S34 deixou pendente (o card já tinha a prop desde S34;
//             agora o FeedPage passa). Se activity.user for null (não
//             deveria — /feed embute user — mas é defensivo), onAuthorTap
//             fica null e o header herda o onTap do card (abre detalhe).
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/activity.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../widgets/activity_card.dart';

class FeedPage extends StatefulWidget {
  final AuthService auth;
  const FeedPage({super.key, required this.auth});

  @override
  State<FeedPage> createState() => _FeedPageState();
}

class _FeedPageState extends State<FeedPage> {
  List<Activity> _activities = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await widget.auth.api.get(
        '/feed?limit=20&offset=0',
        token: widget.auth.token,
      );
      if (!mounted) return;
      final list = (data as List)
          .map((e) => Activity.fromJson(e as Map<String, dynamic>))
          .toList();
      setState(() => _activities = list);
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = 'Erro: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  /// Substitui um item da lista pelo `updated` (mesmo id).
  /// Chamado pelo LikeButton com o estado otimista e, em erro, com o original
  /// (rollback). Como o LikeButton faz o merge, aqui só trocamos o item.
  void _replaceActivity(Activity updated) {
    setState(() {
      _activities = _activities
          .map((a) => a.id == updated.id ? updated : a)
          .toList();
    });
  }

  /// Abre o detalhe e, ao voltar, recarrega o item para refletir
  /// contagens de comentários/crudos feitas lá.
  Future<void> _openDetail(Activity activity) async {
    await context.push('/activity/${activity.id}');
    if (!mounted) return;
    // Recarrega apenas esse item do detalhe para atualizar commentsCount.
    try {
      final data = await widget.auth.api.get(
        '/activities/${activity.id}',
        token: widget.auth.token,
      );
      if (!mounted) return;
      final updated = Activity.fromJson(data as Map<String, dynamic>);
      _replaceActivity(updated);
    } catch (_) {
      // silencioso: se falhar, mantém o estado atual do feed.
    }
  }

  // [Sessão 31] Abre a tela de upload. Se voltar `true`, recarrega o feed
  // inteiro (upload é evento raro — refresh completo é mais simples e
  // correto que refresh de item único, já que a nova atividade pode não
  // estar na página carregada).
  Future<void> _openUpload() async {
    final uploaded = await context.push<bool>('/upload');
    if (!mounted) return;
    if (uploaded == true) {
      _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Feed'),
        // [Sessão 35] Busca de usuários (abre /search, fora do shell).
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            tooltip: 'Buscar',
            onPressed: () => context.push('/search'),
          ),
        ],
      ),
      // [Sessão 31] FAB de upload.
      floatingActionButton: FloatingActionButton(
        onPressed: _openUpload,
        tooltip: 'Enviar atividade',
        child: const Icon(Icons.upload_file),
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
              : _activities.isEmpty
                  ? const Center(child: Text('Nenhuma atividade ainda.'))
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.separated(
                        padding: const EdgeInsets.all(12),
                        itemCount: _activities.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 12),
                        itemBuilder: (context, index) {
                          final a = _activities[index];
                          return ActivityCard(
                            activity: a,
                            auth: widget.auth,
                            onTap: () => _openDetail(a),
                            onChanged: _replaceActivity,
                            // [Sessão 35] Avatar+username abrem o perfil
                            // do autor. Sem user (defensivo), header
                            // herda onTap do card (abre detalhe).
                            onAuthorTap: a.user != null
                                ? () => context.push('/user/${a.user!.id}')
                                : null,
                          );
                        },
                      ),
                    ),
    );
  }
}