HANDOFF — Rumo (backend + frontend + mobile)

Data de encerramento: 2026-11-02 (sessão 7 — Flutter Curtidas + Backend de Contagens validado)
Duração da sessão: Média — correção do ambiente (Docker/venv), alteração no backend para contagens (likes/comments), atualização da API/Mobile e validação total com 111 testes.
Próximo bloco recomendado: Adicionar Comentários no Flutter (Sessão 8).
TL;DR para quem chega agora

    Backend: 111 testes passando. O esquema ActivityResponse (e seus herdeiros) agora embute likes_count, liked_by_me e comments_count diretamente no feed, lista e detalhe. Os services activity_service.py e feed_service.py foram atualizados com subqueries correlacionadas para evitar N+1.

    Frontend Web: React 19 + Vite 8 (inalterado, no ar).

    Mobile: App Flutter (D:\Rumo\mobile) com Curtidas 100% funcional no Feed e no Detalhe. O ApiClient foi expandido (post/delete), o modelo Activity ganhou as contagens e o estado otimista, e o botão de curtir (like_button.dart) foi integrado nas duas telas.

    Commits: O backend (schemas e services) e o mobile (api, model, widget, pages) estão prontos para commit.

    Ambiente: Docker Desktop instalado e configurado no Windows (caminho per-user). Banco de teste rodando na porta 5433.

Produção

    Backend: https://rumo-api-5s0b.onrender.com

    Docs Backend: https://rumo-api-5s0b.onrender.com/docs

    Frontend Web: https://rumo-wheat.vercel.app

    Repo local: D:\Rumo

O que foi feito na Sessão 7
1. Infraestrutura e Ambiente

    O Docker Desktop foi instalado no Windows em modo per-user (C:\Users\nasci\AppData\Local\Programs\DockerDesktop). O PATH do PowerShell teve que ser atualizado manualmente ([Environment]::SetEnvironmentVariable).

    O ambiente virtual Python (.venv) foi recriado/corrigido com pip install -r requirements.txt.

    O banco de testes (PostGIS na porta 5433) foi iniciado via docker compose -f docker-compose.test.yml up -d. Todos os 111 testes passaram.

2. Backend — Contagens Embutidas

    app/schemas/activity.py: Adicionados likes_count, liked_by_me e comments_count ao ActivityResponse.

    app/services/activity_service.py: list_activities, search_activities e get_activity agora usam subqueries correlacionadas e _attach_counts para preencher as contagens sem N+1.

    app/services/feed_service.py: get_feed faz o mesmo para o feed.

3. Mobile — Refatoração da Base

    pubspec.yaml: Confirmadas as versões (Flutter 3.47.9 / Dart 3.13.7). Mantido o padrão de imports atual.

    services/api.dart: Adicionados os métodos post() e delete() (com _send privado para centralizar a lógica de headers e timeout).

    models/activity.dart: Adicionados likesCount, likedByMe e commentsCount (com defaults seguros), além do método copyWith() para o estado otimista.

4. Mobile — Curtidas (Bloco 7.1)

    widgets/like_button.dart (novo): Widget de coração com estado otimista, chamadas POST /like e DELETE /like, e rollback + SnackBar em caso de erro.

    pages/feed_page.dart: Consome GET /feed (antes era /activities) e integra o LikeButton no rodapé do card, com merge de estado via _replaceActivity.

    pages/activity_detail_page.dart: Consome GET /activities/{id} e integra o LikeButton no cabeçalho do autor.

O que não foi feito / Dívidas Técnicas

    Comentários no Flutter: O backend já tem os endpoints (POST/GET/DELETE /comments), mas o mobile ainda não tem UI nem chamadas.

    Mapa: google_maps_flutter ou flutter_map ainda não foram adicionados.

    Limpeza do PATH do Windows: A variável PATH do sistema ainda tem duplicatas (ex.: flutter\bin 3x, Program File truncado). Não afeta o funcionamento, mas vale limpar numa sessão futura.

Próximos Passos Recomendados (Sessão 8) — Comentários no Flutter

O backend já está pronto. O foco será exclusivamente no app Flutter:

    models/comment.dart (novo): Espelhar o CommentResponse do backend (id, activity_id, content, created_at, author).

    services/api.dart: Adicionar métodos listComments(activityId), createComment(activityId, content) e deleteComment(commentId).

    pages/comments_page.dart (ou seção no activity_detail_page.dart):

        Listar comentários (ordem cronológica).

        Campo de input para enviar (POST).

        Botão de deletar (só para o autor do comentário, com DELETE).

    Integração: Adicionar botão de "Comentários" no feed_page.dart (mostrando commentsCount) e a seção de comentários no activity_detail_page.dart.