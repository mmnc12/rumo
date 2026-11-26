// ignore_for_file: unnecessary_overrides
// [Sessão 36] Busca unificada: Usuários + Atividades (paridade com
// SearchPage.tsx do web).
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/activity.dart';
import '../models/user.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../utils/error_message.dart'; // [S48-10.1]
import '../widgets/activity_card.dart';

class SearchPage extends StatelessWidget {
  final AuthService auth;
  const SearchPage({super.key, required this.auth});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Buscar'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Usuários'),
              Tab(text: 'Atividades'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _UserSearchTab(auth: auth),
            _ActivitySearchTab(auth: auth),
          ],
        ),
      ),
    );
  }
}

class _UserSearchTab extends StatefulWidget {
  final AuthService auth;
  const _UserSearchTab({required this.auth});

  @override
  State<_UserSearchTab> createState() => _UserSearchTabState();
}

class _UserSearchTabState extends State<_UserSearchTab>
    with AutomaticKeepAliveClientMixin {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focus = FocusNode();

  Timer? _debounce;

  List<User> _results = const [];
  bool _loading = false;
  String? _error;
  bool _hasSearched = false;

  String get _query => _controller.text;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _focus.requestFocus();
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    _focus.dispose();
    super.dispose();
  }

  void _onQueryChanged(String value) {
    setState(() {});
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 300), _runSearch);
  }

  Future<void> _runSearch() async {
    if (!mounted) return;
    final q = _query.trim();
    if (q.length < 2) {
      setState(() {
        _results = const [];
        _hasSearched = false;
        _loading = false;
        _error = null;
      });
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await widget.auth.api.searchUsers(
        query: q,
        limit: 20,
        token: widget.auth.token,
      );
      if (!mounted) return;
      setState(() {
        _results = list;
        _hasSearched = true;
        _loading = false;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = friendlyErrorMessage(e); // [S48-10.1]
        _loading = false;
        _hasSearched = true;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = friendlyErrorMessage(e); // [S48-10.1]
        _loading = false;
        _hasSearched = true;
      });
    }
  }

  void _clear() {
    _debounce?.cancel();
    _controller.clear();
    setState(() {
      _results = const [];
      _hasSearched = false;
      _loading = false;
      _error = null;
    });
    _focus.requestFocus();
  }

  void _openUser(User user) {
    context.push('/user/${user.id}');
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final theme = Theme.of(context);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
          child: TextField(
            controller: _controller,
            focusNode: _focus,
            onChanged: _onQueryChanged,
            textInputAction: TextInputAction.search,
            onSubmitted: (_) {
              _debounce?.cancel();
              _runSearch();
            },
            decoration: InputDecoration(
              hintText: 'Buscar por usuário (mín. 2 caracteres)',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _query.isEmpty
                  ? null
                  : IconButton(
                      icon: const Icon(Icons.clear),
                      tooltip: 'Limpar',
                      onPressed: _clear,
                    ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              isDense: true,
            ),
          ),
        ),
        Expanded(child: _buildBody(theme)),
      ],
    );
  }

  Widget _buildBody(ThemeData theme) {
    if (_query.trim().length < 2) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'Digite pelo menos 2 caracteres para buscar.',
            textAlign: TextAlign.center,
          ),
        ),
      );
    }
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () {
                  _debounce?.cancel();
                  _runSearch();
                },
                child: const Text('Tentar novamente'),
              ),
            ],
          ),
        ),
      );
    }
    if (_hasSearched && _results.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            'Nenhum usuário encontrado para "${_query.trim()}".',
            textAlign: TextAlign.center,
          ),
        ),
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.all(8),
      itemCount: _results.length,
      separatorBuilder: (_, _) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final u = _results[index];
        return ListTile(
          leading: CircleAvatar(
            backgroundColor: theme.colorScheme.primaryContainer,
            child: Text(
              u.initial,
              style: TextStyle(color: theme.colorScheme.onPrimaryContainer),
            ),
                      ),
          title: Text(u.username),
          subtitle: u.fullName != null && u.fullName!.isNotEmpty
              ? Text(u.fullName!)
              : null,
          onTap: () => _openUser(u),
        );
      },
    );
  }
}

class _ActivitySearchTab extends StatefulWidget {
  final AuthService auth;
  const _ActivitySearchTab({required this.auth});

  @override
  State<_ActivitySearchTab> createState() => _ActivitySearchTabState();
}

class _ActivitySearchTabState extends State<_ActivitySearchTab>
    with AutomaticKeepAliveClientMixin {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focus = FocusNode();

  Timer? _debounce;

  List<Activity> _results = const [];
  bool _loading = false;
  String? _error;
  bool _hasSearched = false;

  String get _query => _controller.text;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    _focus.dispose();
    super.dispose();
  }

  void _onQueryChanged(String value) {
    setState(() {});
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 300), _runSearch);
  }

  Future<void> _runSearch() async {
    if (!mounted) return;
    final q = _query.trim();
    if (q.length < 2) {
      setState(() {
        _results = const [];
        _hasSearched = false;
        _loading = false;
        _error = null;
      });
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await widget.auth.api.searchActivities(
        query: q,
        limit: 20,
        token: widget.auth.token,
      );
      if (!mounted) return;
      setState(() {
        _results = list;
        _hasSearched = true;
        _loading = false;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = friendlyErrorMessage(e); // [S48-10.1]
        _loading = false;
        _hasSearched = true;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = friendlyErrorMessage(e); // [S48-10.1]
        _loading = false;
        _hasSearched = true;
      });
    }
  }

  void _clear() {
    _debounce?.cancel();
    _controller.clear();
    setState(() {
      _results = const [];
      _hasSearched = false;
      _loading = false;
      _error = null;
    });
    _focus.requestFocus();
  }

  void _replaceActivity(Activity updated) {
    setState(() {
      _results = _results
          .map((a) => a.id == updated.id ? updated : a)
          .toList();
    });
  }

  void _openDetail(Activity activity) {
    context.push('/activity/${activity.id}');
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final theme = Theme.of(context);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
          child: TextField(
            controller: _controller,
            focusNode: _focus,
            onChanged: _onQueryChanged,
            textInputAction: TextInputAction.search,
            onSubmitted: (_) {
              _debounce?.cancel();
              _runSearch();
            },
            decoration: InputDecoration(
              hintText: 'Buscar por atividade (mín. 2 caracteres)',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _query.isEmpty
                  ? null
                  : IconButton(
                      icon: const Icon(Icons.clear),
                      tooltip: 'Limpar',
                      onPressed: _clear,
                    ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              isDense: true,
            ),
          ),
        ),
        Expanded(child: _buildBody(theme)),
      ],
    );
  }

  Widget _buildBody(ThemeData theme) {
    if (_query.trim().length < 2) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'Digite pelo menos 2 caracteres para buscar.',
            textAlign: TextAlign.center,
          ),
        ),
      );
    }
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () {
                  _debounce?.cancel();
                  _runSearch();
                },
                child: const Text('Tentar novamente'),
              ),
            ],
          ),
        ),
      );
    }
    if (_hasSearched && _results.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            'Nenhuma atividade encontrada para "${_query.trim()}".',
            textAlign: TextAlign.center,
          ),
        ),
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: _results.length,
      separatorBuilder: (_, _) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final a = _results[index];
        return ActivityCard(
          activity: a,
          auth: widget.auth,
          onTap: () => _openDetail(a),
          onChanged: _replaceActivity,
          onAuthorTap: a.user != null
              ? () => context.push('/user/${a.user!.id}')
              : null,
        );
      },
    );
  }
}