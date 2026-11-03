HANDOFF — Rumo (backend + frontend + mobile)

Data de encerramento: 2026-11-02 (sessão 8 — Comentários no Flutter validados em runtime)
Duração da sessão: Média — implementação completa de comentários no mobile (model, API, UI no detalhe, contador no feed), correção de PATH do Flutter, analyze zerado e validação manual ponta a ponta.
Próximo bloco recomendado: Mapa no Flutter (Sessão 9) — recomendo flutter_map (sem API key).
Decisão para a Sessão 9: seguir com Mapa no Flutter via flutter_map, salvo se o usuário indicar outra prioridade. Primeira ação obrigatória: confirmar coordenadas no backend antes de alterar o pubspec.yaml.
TL;DR para quem chega agora

    Backend: 111 testes passando. ActivityResponse embute likes_count, liked_by_me e comments_count no feed, lista e detalhe (subqueries correlacionadas, sem N+1). Endpoints de comentários (POST/GET/DELETE) prontos e validados.

    Frontend Web: React 19 + Vite 8 (inalterado, no ar).

    Mobile: App Flutter (D:\Rumo\mobile) com Curtidas e Comentários 100% funcionais.
        Curtidas: LikeButton com estado otimista no feed e no detalhe (Sessão 7).
        Comentários: model Comment, métodos listComments/createComment/deleteComment no ApiClient, seção completa no activity_detail_page.dart (listar, criar, deletar só o próprio) e contador/botão no card do feed_page.dart com refresh ao voltar do detalhe.

    Qualidade: flutter analyze => "No issues found!" (0 issues).

    Ambiente: Flutter 3.47.9 / Dart 3.13.7. PATH do Windows corrigido (C:\Users\nasci\flutter\bin no PATH do usuário) — a dívida de PATH duplicado foi resolvida.

    Commits: estado da Sessão 7 já commitado. Sessão 8 pronta para commit (ver seção "Commits pendentes").

Produção

    Backend: https://rumo-api-5s0b.onrender.com
    Docs Backend: https://rumo-api-5s0b.onrender.com/docs
    Frontend Web: https://rumo-wheat.vercel.app
    Repo local: D:\Rumo

O que foi feito na Sessão 8
1. Model — mobile/lib/models/comment.dart (novo)

    Espelha CommentResponse do backend: id, activity_id, content, created_at, updated_at, author.
    author reusa UserPublic (mesmo modelo do Activity), sem duplicação.
    copyWith (content/updatedAt/author) e helper canDelete(currentUserId) para esconder o botão de excluir de quem não é autor.

2. API — mobile/lib/services/api.dart

    Adicionados: listComments(activityId), createComment(activityId, content) e deleteComment(commentId).
    Reutilizam o _send/post/delete existentes (headers, timeout, decode centralizados). Nada do que já funcionava foi alterado.

3. UI — mobile/lib/pages/activity_detail_page.dart

    Seção de comentários no detalhe: lista cronológica, input (max 500, envio por botão e por Enter), botão de excluir visível só para o autor.
    Contador "Comentários (N)" atualizado localmente ao criar/deletar (sem recarregar a atividade).
    Id do usuário atual obtido decodificando o sub do JWT (widget.auth.token) — não depende de getter no AuthService.

4. Feed — mobile/lib/pages/feed_page.dart

    Botão de comentários no rodapé do card, ao lado do LikeButton, exibindo commentsCount e navegando para o detalhe.
    _openDetail: ao voltar do detalhe, refaz GET /activities/{id} e atualiza só aquele item no feed (contadores em dia). Falha silenciosa.

5. Qualidade e ambiente

    flutter analyze: 0 issues (corrigidos 3 lints unnecessary_underscores em main.dart e feed_page.dart).
    PATH do Flutter corrigido: C:\Users\nasci\flutter\bin adicionado ao PATH do usuário; flutter --version e flutter analyze funcionando no PowerShell.
    Validação manual ponta a ponta OK: listar, criar, deletar (só o autor) e contador do feed atualizando ao voltar do detalhe.

Commits pendentes (Sessão 8 — recomendo 1 commit único de feature)

    cd D:\Rumo
    git add mobile/lib/models/comment.dart mobile/lib/services/api.dart mobile/lib/pages/activity_detail_page.dart mobile/lib/pages/feed_page.dart mobile/lib/main.dart
    git commit -m "feat(mobile): comentários no detalhe e contador no feed (model, API, UI, delete do autor, analyze zerado)"

O que não foi feito / Dívidas Técnicas

    Mapa: flutter_map ou google_maps_flutter ainda não adicionados. (Próximo bloco recomendado.)
    Getter currentUserId no AuthService: hoje a página decodifica o JWT localmente. Vale mover para um getter único no AuthService numa sessão futura (limpeza, não bloqueia nada).
    Validação dos paths de comentário: funcionou em runtime com GET/POST /activities/{id}/comments e DELETE /comments/{id}; se o backend mudar o path do DELETE, é ajuste de string só no api.dart.
    Limpeza do PATH do Windows: resolvido o essencial (flutter no PATH). A limpeza de duplicatas antigas (flutter\bin 3x, "Program File" truncado) deixou de ser necessária para o funcionamento; pode ser feita por estética numa sessão futura, se desejado.

Próximos Passos Recomendados (Sessão 9) — Mapa no Flutter

Decisão para a Sessão 9: seguir com Mapa no Flutter via flutter_map, salvo se o usuário indicar outra prioridade. Primeira ação obrigatória: confirmar coordenadas no backend antes de alterar o pubspec.yaml.

Recomendação: usar flutter_map (leve, sem API key, OpenStreetMap) em vez de google_maps_flutter (exige chave paga e config de plataforma).

    pubspec.yaml: adicionar flutter_map e latlong2.
    Backend: confirmar se Activity já expõe coordenadas (lat/lng ou GeoJSON). Se não, avaliar adicionar ao ActivityResponse (ou endpoint de track/rota).
    models/activity.dart: incluir campos de coordenada (com defaults seguros), se vierem do backend.
    widgets/activity_map.dart (novo): mapa somente-leitura com marcador do início (e polyline da rota, se houver track).
    Integração: exibir o mapa no activity_detail_page.dart (card "Rota") e, opcionalmente, miniatura no feed.
    Sem quebrar o existente: manter o padrão atual (ApiClient, auth, estados de loading/erro) e rodar flutter analyze ao final (meta: 0 issues).