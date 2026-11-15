// [Sessão 35] Busca de usuários por username/full_name.
//
// Porta a aba "Usuários" da SearchPage.tsx do web (a aba "Atividades" fica
// para uma sessão futura). Fluxo: usuário digita ≥2 chars → debounce 300ms
// (paridade com useDebounce do web) → GET /users/search?q=&limit=20 →
// lista de User → onTap abre /user/:id (UserProfilePage da S34).
//
// Decisões de UX/semântica herdadas do web (fonte da verdade):
// - Mínimo 2 caracteres (o useUserSearch do web usa enabled: len>=2).
// - Debounce 300ms (useDebounce do web usa 300).
// - limit=20 (useUserSearch do web usa limit=20).
// - TextField recebe autoFocus, prefixIcon search, suffixIcon clear.
// - "Nenhum usuário encontrado" só aparece DEPOIS de uma busca real
//   (hasSearched), pra não confundir com o estado inicial vazio.
//
// O que NÃO replicamos do web (escopo desta sessão):
// - Deep-link ?q= na URL (o /search mobile é fluxo efêmero, YAGNI).
// - Aba "Atividades" (fica pra S36; o web mistura, aqui separamos).
// - Sincronização do termo com a URL (replace:true no web) — não há URL.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/user.dart';
import '../services/api.dart';
import '../services/auth_service.dart';

class UserSearchPage extends StatefulWidget {
  final AuthService auth;
  const UserSearchPage({super.key, required this.auth});

  @override
  State<UserSearchPage> createState() => _UserSearchPageState();
}

class _UserSearchPageState extends State<UserSearchPage> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focus = FocusNode();

  Timer? _debounce;

  List<User> _results = const [];
  bool _loading = false;
  String? _error;
  bool _hasSearched = false;

  String get _query => _controller.text;

  @override
  void initState() {
    super.initState();
    // Foco imediato — paridade com autoFocus do web.
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
    setState(() {
      // Atualiza o sufixo (clear) e o estado do body enquanto digita.
      // Não mexemos em _results/_error aqui — o debounce cuida disso.
    });
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
        _error = e.message;
        _loading = false;
        _hasSearched = true;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Erro: $e';
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
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Buscar'),
      ),
      body: Column(
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
      ),
    );
  }

  Widget _buildBody(ThemeData theme) {
    // Estado inicial: menos de 2 chars digitados.
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

    // Buscando.
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    // Erro (rede, 429, 500).
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

    // Buscou e veio vazio.
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

    // Resultados.
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