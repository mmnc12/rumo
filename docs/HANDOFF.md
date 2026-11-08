HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 22
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação sobre o projeto chega por DUAS vias:

(a) o usuário cola o conteúdo de um arquivo com Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal

NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere o usuário colar. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

Sessões anteriores perderam tempo porque o assistente tentou "adivinhar" a árvore de diretórios e errou. Não repetir.
⚠️ REGRA S21 — nunca placeholder no código entregue

A S21 teve dois tropeços causados pela mesma causa raiz: eu entreguei um bloco com # ... (resto do arquivo INALTERADO ...) como "rascunho didático". O usuário colou no activity_service.py (arquivo grande) e sobrescreveu tudo. Recuperado com git restore.

Regra permanente: quando eu não tiver o conteúdo de um arquivo existente, NÃO entrego nem "rascunho de bloco". Peço o arquivo (Get-Content -Encoding UTF8) e só entrego completo, pronto para Ctrl+A → colar → salvar. Nunca marcador no meio do código. É o único jeito de eliminar esse tipo de erro.
⚠️ REGRA S21 — não adivinhar nomes de símbolos do projeto

No test_export.py, escrevi ActivityType.run (era ActivityType.RUN) e Follow(followed_id=...) (era following_id=...). O ruff não pega (é semântico, não sintático) — só o pytest pegou.

Regra permanente: antes de escrever teste ou código que referencia símbolo de model/enum/schema do projeto, peça o arquivo (models/activity.py, models/follow.py, schemas/activity.py, etc.). É barato (são pequenos) e elimina a classe de erro.
⚠️ REGRA S21 — git status antes de qualquer git restore/git checkout

Sempre rodar git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo> antes de tentar restaurar. Se o último commit que tocou o arquivo for anterior à mudança quebrada, git checkout/git restore restaura. Se a versão quebrada já foi commitada, git show <commit-anterior>:<caminho> > <caminho> é o caminho.
⚠️ REGRA S22 (nova) — Invoke-WebRequest com -UseBasicParsing

O PowerShell 5.1 emite prompt de segurança ("Risco de Execução de Script") em Invoke-WebRequest sem -UseBasicParsing. Sempre entregar Invoke-WebRequest com -UseBasicParsing — elimina o prompt e não muda nada para CSV/GPX/ZIP (texto/binário puro). O usuário respondia a (Sim para Todos) — funciona, mas é atrito desnecessário.
⚠️ REGRA S22 (nova) — validar deploy do Render antes de acusar bug no código

Na S22, os primeiros Invoke-WebRequest para /activities/export retornaram 422 e eu quase abri diagnóstico de bug. Causa: o Render ainda não tinha terminado o redeploy do commit. A rota nova ainda não estava no ar; o /{activity_id} casava com "export" como UUID inválido e dava 422.

Regra permanente: depois de git push, aguardar o redeploy do Render terminar antes de validar produção. Sinal objetivo: Invoke-RestMethod https://rumo-api-5s0b.onrender.com/openapi.json | Select-String "<rota nova>" — se a rota aparecer no openapi.json, o deploy está no ar. Alternativa: olhar o dashboard do Render (rumo-api → "Events"/"Deploys") e ver o commit como Live. Se der 404/422 em rota nova após push, primeiro checar openapi.json, depois acusar código.
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos — o usuário precisa colar conteúdo e saídas de terminal.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app). Backend de produção usa Postgres/PostGIS gerenciado. Testar via HTTP é sempre possível.

IMPORTANTE — usuário NÃO tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam automaticamente, validar via HTTP em produção. Não presumir que o usuário vai "rodar o app localmente" para testar UI.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (164 passed ao fim da S22 — 153 + 11 novos do export em lote). Container de teste rumo_postgres_test na porta 5433.

⚠️ ATENÇÃO — docker ps sozinho esconde container parado. Na abertura da S21, pytest -q falhou com 126 erros de ConnectionRefusedError: [WinError 1225] porque o container rumo_postgres_test estava Exited (255). docker ps -a --filter "name=rumo_postgres_test" mostrou Exited; up -d subiu; pg_isready respondeu accepting connections; pytest voltou a 143 (na S21). Primeira verificação da S23+ deve ser docker ps -a --filter "name=rumo_postgres_test" (com -a), não só docker ps.

Para reativar numa sessão nova:

    Abrir Docker Desktop e esperar a baleia verde.

    Garantir que o terminal foi aberto via Win+R (fora do VS Code / Windows Terminal, que herdam PATH antigo).

    cd D:\Rumo\backend

    docker compose -f docker-compose.test.yml up -d

    docker ps -a --filter "name=rumo_postgres_test" (deve mostrar Up … (healthy))

    docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432 (deve dizer accepting connections)

    .\venv\Scripts\Activate.ps1 (UM ponto, não dois)

    python -m pytest -q

VENV: ao fim da S22, a única venv é D:\Rumo\backend\venv (sem ponto), Python 3.13.7. .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"].

ATENÇÃO: py -3 deste Windows aponta para Python 3.14 (incompatível com requirements.txt). Se precisar recriar a venv: py -3.13 -m venv D:\Rumo\backend\venv ou C:\Python313\python.exe -m venv D:\Rumo\backend\venv.
Estrutura do repo (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada na Sessão 19 e inalterada em estrutura na S20/S21/S22 (só arquivos modificados/criados, nenhum removido):
text

D:\Rumo
├── .vscode
│   └── settings.json
├── backend
│   ├── .pytest_cache
│   ├── .ruff_cache
│   ├── venv\                      # ATIVA (Python 3.13.7)
│   ├── alembic
│   ├── app
│   │   ├── core
│   │   ├── models                  # activity.py, follow.py, user.py, like.py,
│   │   │                          # comment.py, notification.py, activity_photo.py
│   │   ├── routers\               # activities.py, auth.py, comments.py, feed.py,
│   │   │                          # notifications.py, photos.py, users.py, __init__.py
│   │   ├── schemas\               # activity.py, like.py, stats.py, user.py, ...
│   │   ├── services\              # activity_service.py, comment_service.py, errors.py,
│   │   │                          # feed_service.py, fit_service.py, follow_service.py,
│   │   │                          # gpx_service.py, like_service.py, notification_service.py,
│   │   │                          # photo_service.py, stats_service.py, user_service.py
│   │   └── __pycache__
│   ├── samples
│   ├── scripts
│   ├── tests\                     # conftest.py + test_calories.py + test_comment.py +
│   │                              # test_export.py + test_export_bulk.py (NOVO S22)
│   │                              # + test_follow.py + test_like.py + test_stats.py + __init__.py
│   ├── _scratch
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
├── docs
│   └── HANDOFF.md
├── mobile
│   └── lib
│       ├── models\                # activity.dart, activity_track.dart, comment.dart
│       ├── pages\                 # activity_detail_page.dart, feed_page.dart, login_page.dart
│       ├── services
│       └── widgets\               # activity_map.dart, like_button.dart
└── web
    └── src
        ├── api\                   # activities.ts, auth.ts, client.ts, notifications.ts,
        │                          # photos.ts, social.ts, stats.ts
        ├── assets
        ├── components\            # ActivityCard, ActivityResults, AppHeader, CommentsSection,
        │                          # LikeButton, NotificationBell, PeriodChart, PhotoGallery,
        │                          # PhotoUpload, ProtectedRoute, RouteMap, StatsCards, UserResults
        ├── contexts
        ├── hooks\                 # useActivities, useActivitySearch, useAuth, useDebounce,
        │                          # useNotifications, usePhotos, useProfile, useSocial,
        │                          # useStats, useUserSearch
        ├── lib\                   # format.ts, geo.ts
        ├── pages\                 # ActivitiesPage, ActivityDetailPage, FeedPage, LoginPage,
        │                          # NotificationsPage, ProfilePage, RegisterPage, SearchPage, UploadPage
        └── types\                 # api.ts

Como rodar comandos Flutter no Windows deste usuário

Flutter instalado em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7 / DevTools 2.60.0.

PROBLEMA CONHECIDO: mesmo com C:\Users\nasci\flutter\bin no PATH, o PowerShell frequentemente NÃO reconhece flutter (cache de sessão). SOLUÇÃO QUE FUNCIONA: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Como rodar Docker e pytest local (Windows deste usuário)

Docker Desktop instalado em C:\Users\nasci\AppData\Local\Programs\DockerDesktop. Se docker não for reconhecido, abrir PowerShell via Win+R → powershell.

Container de teste: rumo_postgres_test (5433). Containers permanentes rumo-redis (6379) e rumo-postgres (5432) NÃO são de teste.
Como testar o backend de produção sem o app (PowerShell)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me. /users/me devolve 422.
powershell

$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id

Contas de teste:

    prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341 (6 atividades, 26.443 m).

    Prod2 (id 01a141e7-5ea4-7600-8959-19145475ad0a) — 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

    Para o cenário "terceiro NÃO seguido": usar a busca (/users/search?q=a) e escolher um id que não seja prod nem Prod2.

⚠️ Lições S18–S22 — detecção de versão no ar:

    422 de versão NÃO distingue S17 de S18. /activities/stats/by-type?period=30d devolve 422 desde a S17.

    Para S19: GET /users/{meId}/stats/summary responde 200 (não 404) e GET /users/me responde 422.

    Para S20: GET /activities/stats/by-type?period=90d&compare=yoy responde 200. E ?compare=xpto responde 422.

    Para S21: GET /activities/{id}/export?format=csv e ?format=gpx respondem 200; ?format=xpto responde 422. Se der 404 em format=csv num id válido, o backend ainda está na S20.

    Para S22: GET /activities/export?format=csv responde 200 application/zip (ZIP com N .csv dentro); GET /activities/export?format=gpx responde 200 application/zip (só com rota); ?format=xpto responde 422; ?from=2099-01-01 responde 200 com ZIP vazio (0 entries); ?from=2026-12-01&to=2026-01-01 responde 422. Se der 422 em format=csv sem filtro, checar openapi.json primeiro (deploy do Render pode não ter terminado).

⚠️ Lição S20/S21/S22 — previous: null em prod/Prod2 não é bug. Nenhuma das contas de teste tem atividade na janela de comparação. Os 164 testes locais provam que a janela funciona.
O que o assistente precisa pedir ao usuário (não tem acesso a arquivos)

    Conteúdo de arquivos via Get-Content -Encoding UTF8 <caminho>. SEMPRE passar -Encoding UTF8; sem isso, acentos viram inÃ­cio.

    Saídas de comandos (flutter analyze, npm run build, git log, git status, pytest -q, ruff check).

    Nunca assumir estrutura "de cabeça": pedir o arquivo antes de reescrevê-lo.

ATENÇÃO — arquivos truncados/duplicados: se um Get-Content vier com a última linha cortada OU com o conteúdo DUPLICADO, NÃO adivinhar o final. Pedir ruff check <arquivo> (lista duplicatas de uma vez) e entregar o arquivo completo para Ctrl+A → colar → salvar.

ATENÇÃO — arquivo "salvo" que não salvou. SINTOMA: build ou pytest falha dizendo que um símbolo novo não existe, mesmo o assistente tendo entregado o arquivo. DIAGNÓSTICO: Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>". Se não aparecer, o disco ainda é o antigo. REGRA: depois de entregar um arquivo que muda contrato, pedir a confirmação com Get-Content | Select-String antes de rodar build/test.

ATENÇÃO — git diff pipeado no PowerShell pode exibir acentos como mojibake. Artefato de codepage do pipe, NÃO corrupção.

ATENÇÃO — git log --oneline no PowerShell às vezes cola a última linha com o prompt. Formatação, não corrupção.

ATENÇÃO — git log sem --no-pager abre o less e trava o terminal. SEMPRE usar git --no-pager log ... ou prefixar com $env:PAGER="".

ATENÇÃO — Pylance reclamando de imports (fastapi/sqlalchemy/pytest) NÃO é erro de código. Interpretador errado. Causa raiz corrigida na S20: .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"]. Se voltar: Ctrl+Shift+P → "Python: Select Interpreter" → D:\Rumo\backend\venv\Scripts\python.exe → Developer: Reload Window.

ATENÇÃO — Invoke-WebRequest sem -UseBasicParsing pergunta sobre risco de execução de script. Responder a (Sim para Todos) funciona, mas entregar Invoke-WebRequest sempre com -UseBasicParsing elimina o prompt.

ATENÇÃO — validar openapi.json antes de acusar bug em rota nova. Se git push acabou de acontecer e uma rota nova responde 422/404, é quase certo que o Render ainda não redeployou. Rodar Invoke-RestMethod https://rumo-api-5s0b.onrender.com/openapi.json e procurar a rota; se não aparecer, Manual Deploy no Render ou aguardar. Confirmado na S22.
Acordos de trabalho (válidos em todas as sessões — REFORÇADOS na S21/S22)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário. (Usuário reforçou nas S15–S22.) O assistente decide e recomenda; não fica perguntando "qual opção você prefere?".

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder no meio do código. Preservar imports, comentários e trechos que já funcionam. Destacar o trecho alterado com comentário curto acima (// [Sessão N] ou // [Sessão N — fix]).

    UMA versão por arquivo por resposta. Se errar no meio do raciocínio, cortar a versão errada e entregar só a corrigida com nota de 1 linha. NUNCA duas versões do mesmo arquivo na mesma resposta.

    HANDOFF PREVENTIVO em ~70–80% do limite de contexto: parar o trabalho em curso e entregar o HANDOFF completo neste mesmo formato (seções 0 a 9), pronto para colar no próximo chat. Deve ser COMPLETO e bem explicado, não resumido.

    VALIDAÇÃO INCREMENTAL: quando a mudança toca mais de um arquivo da mesma stack, colar o(s) arquivo(s) base e rodar build/analyze antes de entregar o próximo — reduz superfície de erro. Exceção legítima: 2 arquivos acoplados por mudança de contrato interno (ex.: hook + consumidor do hook). Nesse caso, entregar os 2 juntos e rodar 1 build.

    VERIFICAR SAVE ANTES DE BUILD: quando o assistente entrega um arquivo com símbolo novo (tipo, função, param), pedir ao usuário Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>" antes de rodar build/test.

    (S21) NUNCA placeholder no código entregue. Se o assistente não tem o conteúdo de um arquivo existente, peça e espere — não entregue "rascunho de bloco".

    (S21) Não adivinhar nomes de símbolos. Antes de referenciar ActivityType.X, Follow(...), campos de schema, etc., peça o arquivo do model/enum/schema. ruff não pega, pytest pega com traceback claro — mas custa ida e volta.

    (S21) Antes de git restore/git checkout, rodar git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>. Confirmar que o último commit que tocou o arquivo é anterior à mudança quebrada.

    (S22) Invoke-WebRequest sempre com -UseBasicParsing.

    (S22) Depois de git push, aguardar redeploy do Render e validar openapi.json antes de acusar bug em rota nova.

Processo que o usuário elogiou na S21/S22 (para manter)

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho." O que funcionou:

    Ordem clara: Fase 0 (validação de estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 4 (validação em produção) → Fase 5 (handoff).

    Descoberta antes de codar: pedir os arquivos com motivo declarado. Cada pedido justificado.

    Validação entre cada entrega: Select-String (save) + ruff + pytest no backend; npm run build + npm run lint no front. Nunca acumular 2 arquivos sem validar.

    Contrato travado escrito antes de codar: endpoint, auth, 404 vs 422, headers, formato CSV/GPX/ZIP. O usuário lê e aprova tacitamente.

    Commits pequenos e temáticos: docs: handoff da Sessao N, feat(activities): ..., feat(web): ....

    Validação em produção separada da local: local verde é pré-requisito, mas prod via HTTP/browser é o que fecha.

    (S22) Diagnóstico honesto antes de "consertar": quando o 422 apareceu em /activities/export, o correto foi pedir o BODY da resposta e o openapi.json — não presumir bug. Causa era deploy em andamento.

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 164 testes passando LOCALMENTE (pytest -q verde na Sessão 22 — 153 + 11 novos do export em lote), 0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon,minLat,maxLon,maxLat], n_points, simplified. 404 quando route é NULL.

ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax do PostGIS no mesmo SELECT (sem N+1). None quando route é NULL.

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.

Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (helper _ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Export unitário (S21): GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor (mesma regra do /track; senão 404). Response com Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>". CSV: text/csv; charset=utf-8, 1 header + 1 linha (funciona sem rota, bbox_* vazios). GPX: application/gpx+xml; charset=utf-8, exige rota (404 "Atividade não possui rota"). format inválido → 422. format omitido → default csv.

NOVO na S22 — Export em lote:

    GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — auth self-only (só atividades do próprio viewer; diferente do unitário, que aceita seguidor).

    Saída é ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip") com N arquivos dentro, cada um no formato unitário (rumo_<id>_<type>.csv ou .gpx).

    format=csv: inclui todas as atividades do filtro (com ou sem rota).

    format=gpx: inclui só atividades com rota (as sem rota são omitidas — não gera GPX vazio).

    Filtro from/to (YYYY-MM-DD, UTC, inclusivo nas duas pontas; to inclui o dia inteiro).

    0 atividades no filtro → 200 com ZIP vazio (0 entries). from > to → 422 ("from deve ser <= to"). format inválido → 422.

    Reusa get_activity, get_activity_track, _activity_to_csv, _export_filename, to_gpx da S21. Nada existente mudou.

Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet (RouteMap no detalhe) + recharts (gráficos no perfil). Drill-down por tipo tem segmented control de janela temporal (S17), coluna "vs. anterior" com delta colorido (S18), 2º segmented control "Comparar com:" (prev/yoy) que só aparece quando period !== "all" (S20). S21: botões "Baixar CSV" (sempre) e "Baixar GPX" (condicional a track) no cabeçalho do ActivityDetailPage. Helper apiFetchBlob em client.ts (aditivo, não mexe no apiFetch). downloadActivityExport(id, format) em activities.ts. S22 não tocou no front (front "Exportar tudo" fica para S23).

Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite), alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds. Intocado desde a S11. Sem drill-down de stats no app. Sem export no app.
Entregas da Sessão 22 (backend — export em lote CSV/GPX em ZIP)

activity_service.py:

    Topo: + import zipfile, + from datetime import date, datetime, time, timedelta, timezone (bloco novo). Só adições — resto do arquivo idêntico à S21.

    Fim: bloco novo # ----- Export em lote (ZIP) — [Sessão 22] ----- com:

        _bulk_export_filename(now) -> str — rumo_export_<YYYYMMDD-HHMMSS>.zip.

        _to_utc_start(d: date) -> datetime — datetime.combine(d, time.min, tzinfo=timezone.utc).

        async _get_user_activity_ids_in_range(db, user_id, date_from, date_to) -> list — select(Activity.id) com filtro started_at opcional; ValueError("from deve ser <= to") se from > to; ordenação started_at DESC.

        async export_activities_bulk(db, viewer_id, fmt, date_from=None, date_to=None) -> tuple[bytes, str, str] — monta zipfile.ZipFile em BytesIO com ZIP_DEFLATED; CSV inclui todas; GPX omite sem rota (except NotFoundError: continue); retorna (zip_bytes, "application/zip", filename).

routers/activities.py:

    Topo: + from datetime import date.

    Nova rota GET /export inserida entre GET "" (list_activities) e GET /{activity_id} (bloco "rotas estáticas", mesma convenção de /stats/* e /search). Parâmetros: format: Literal["csv","gpx"]="csv", from_: date | None = Query(alias="from"), to_: date | None = Query(alias="to"). try/except ValueError → HTTPException(422, detail=str(exc)); except ServiceError → HTTPException. Resposta Response(content, media_type, {"Content-Disposition": ...}).

tests/test_export_bulk.py (NOVO): 11 testes:

    test_export_bulk_csv_owner_ok — 2 atividades → ZIP com 2 .csv, header + 1 linha cada, valores batem.

    test_export_bulk_csv_includes_no_route — atividade sem rota entra no CSV (bbox_* vazios).

    test_export_bulk_csv_only_own_activities — atividades de outro usuário não entram (self-only).

    test_export_bulk_gpx_skips_no_route — 1 com rota + 1 sem → ZIP só com 1 .gpx. Prova inversão [lon,lat]→lat/lon comparando com raw_track_points (mesma técnica da S21).

    test_export_bulk_gpx_all_no_route_empty_zip — só sem rota + format=gpx → ZIP vazio (0 entries), 200.

    test_export_bulk_empty_user_ok — usuário sem atividades → ZIP vazio, 200.

    test_export_bulk_date_from_filter — from=2024-02-01 corta as anteriores.

    test_export_bulk_date_to_filter — to=2024-02-29 inclui o dia inteiro (atividade de 23:59 UTC incluída, de 00:01 do dia seguinte excluída).

    test_export_bulk_from_after_to_422 — from > to → 422, detail contém "from".

    test_export_bulk_invalid_format_422 — format=xpto → 422.

    test_export_bulk_default_format_is_csv — sem ?format → ZIP de .csv.

    Helper _client_as(user, test_engine) idêntico ao de test_export.py (S21) — sobrescreve get_db E get_current_user. _create_activity_with_date para started_at controlado. _read_zip_entries(content) -> dict[str, bytes] para inspecionar entradas.

Estado final da S22: working tree limpo após o commit do backend. HEAD == origin/main == 6cce475 (backend S22) — aguardando o commit do HANDOFF da S22 (a fazer logo abaixo).

Render: /activities/export validado em produção (ZIP 200, 6 entries no CSV e no GPX, 0 entries no filtro futuro, 422 em xpto e em from>to).

Vercel: front não mudou na S22. Nenhum redeploy novo esperado.
SEÇÃO 2 — PRODUÇÃO E AMBIENTE

    Backend: https://rumo-api-5s0b.onrender.com

    Docs Backend: https://rumo-api-5s0b.onrender.com/docs

    Frontend Web: https://rumo-wheat.vercel.app

    Repo local: D:\Rumo

    Mobile: D:\Rumo\mobile

    Web: D:\Rumo\web (scripts: "build": "tsc -b && vite build", "lint": "eslint .")

    Flutter: 3.47.9 / Dart 3.13.7

    Docker Desktop: 4.93.0 (engine 29.8.1, compose v5.5.1)

    SO: Windows, PowerShell 5.1

    Python: 3.13.7 (venv em D:\Rumo\backend\venv) — NÃO usar 3.14

    Venv backend: D:\Rumo\backend\venv (ativa com .\venv\Scripts\Activate.ps1)

    Deps novas em S22: nenhuma (zipfile é stdlib).

Git (estado ao fim da Sessão 22, ANTES do commit do handoff)
text

6cce475 (HEAD -> main, origin/main) feat(activities): export em lote CSV/GPX em ZIP (Sessao 22)
ad7b99a docs: handoff da Sessao 21
ee3215b feat(web): botoes baixar CSV/GPX no detalhe (Sessao 21)
8936415 feat(activities): export CSV/GPX (Sessao 21)
19ebc3b docs: handoff da Sessao 20
2ca4c81 feat(web): toggle year-over-year no drill-down por tipo (Sessao 20)
879d885 feat(stats): comparacao year-over-year no drill-down por tipo (Sessao 20)
09a6596 docs: handoff da Sessao 19

Pendente: docs/HANDOFF.md da S22 (este arquivo) — o usuário vai salvar e commitar como docs: handoff da Sessao 22 (instruções no fim).
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 22
3.1 Validação de estado inicial

PowerShell via Win+R. git push → Everything up-to-date. HEAD == origin/main == ee3215b (S21 front commitado em ee3215b — a pendência de commit do front que o handoff da S21 previa já estava resolvida). git status --short mostrou só M docs/HANDOFF.md (handoff da S21 não commitado — herdado).

Ação 1: commit do handoff S21 (ad7b99a docs: handoff da Sessao 21) + push.

Ação 2 (sanidade de build): npm run build → 824 modules, ActivityDetailPage 13.00 kB (idêntico ao S21 → confirma que o front commitado é o mesmo que rodou); npm run lint → limpo; flutter analyze → No issues found.

Ação 3 (Docker + pytest): docker ps -a --filter "name=rumo_postgres_test" mostrou Up 3 hours (healthy) (não precisou up -d); pg_isready OK; pytest -q → 153 passed (44.55s); ruff check . → All checks passed.
3.2 Ação 4 — validação em produção (S21: export unitário)

Invoke-WebRequest para /activities/{id}/export?format=csv e ?format=gpx na conta prod. Resultados:

    CSV: 200 text/csv; charset=utf-8, 1 header + 1 linha, bbox preenchido, elevation_gain_m/avg_pace_s_per_km/avg_speed_mps vazios.

    GPX: 200 application/gpx+xml; charset=utf-8, <gpx><trk><name>….

    format=xpto → 422.

Prompt de segurança do Invoke-WebRequest apareceu (sem -UseBasicParsing) — usuário respondeu a. Regra S22 registrada.
3.3 Ação 5 — validação visual do front S21

Usuário confirmou "tudo funcionando como esperado" (botões "Baixar CSV"/"Baixar GPX" no detalhe, GPX condicional a rota, downloads ok, GPX desenhou no gpx.studio, CSV abre com 2 linhas e bbox preenchido). Sessão 21 oficialmente 100% validada em produção.
3.4 Contrato travado da S22 (OPÇÃO 1 — export em lote)

Apresentado e aprovado tacitamente ("sempre seguir recomendação"). Ponto decisivo: ZIP em vez de concatenado. Motivos:

    GPX concatenado é inválido (um <gpx> raiz por arquivo); N atividades → N arquivos.

    CSV concatenado é ambíguo se colunas variarem no futuro.

    ZIP é o padrão de serviços de export (Strava, Garmin Connect).

    Usuário abre e tem N arquivos prontos para importar.

Decisões travadas:

    Auth: self-only (diferente do unitário).

    format=csv: todas (com ou sem rota).

    format=gpx: só com rota (omite sem rota).

    Filtro from/to: YYYY-MM-DD, UTC, inclusivo; to inclui dia inteiro.

    0 atividades → 200 + ZIP vazio.

    from > to → 422.

    format inválido → 422.

    Header: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip".

3.5 Fase 1 — descoberta (pedidos com motivo)

Pedidos ao usuário (todos com motivo declarado):

    activity_service.py topo+fim → ver imports e bloco S21 a reusar.

    routers/activities.py inteiro → ver ordem das rotas (/export antes de /{activity_id}) e import Response.

    schemas/activity.py primeiras 120 linhas → ActivityResponse/TrackResponse.

    models/activity.py inteiro → ActivityType UPPER_CASE, started_at timezone-aware, route, raw_track_points.

    test_export.py inteiro → reusar _client_as (que sobrescreve get_db e get_current_user).

    conftest.py inteiro → fixtures client, test_engine, test_user, sample_gpx_bytes.

Depois: pedi o activity_service.py inteiro (não só topo+fim) antes de entregar a versão completa (regra S21 — nunca placeholder).
3.6 Fase 2.5 — ajustes contra o código real

3 ajustes identificados lendo o código real:

    Ajuste 1: bbox é setattr feito por _attach_counts (não coluna ORM). Solução: no lote, iterar IDs → get_activity por ID (preenche bbox) → _activity_to_csv. Custo O(N) queries aceitável.

    Ajuste 2: filtro de data no WHERE do select(Activity.id) (usa índice ix_activities_user_started), não em Python.

    Ajuste 3: GPX em lote chama get_activity_track por atividade (herda o 404 "sem rota"), e except NotFoundError: continue (omitir é o comportamento documentado).

3.7 Fase 3 — entrega incremental

Arquivo 1/3 — activity_service.py completo. Topo + import zipfile + from datetime import .... Fim: bloco # ----- Export em lote (ZIP) — [Sessão 22] ----- com 4 funções novas. Validação: Select-String (confirmou 3 funções + import zipfile); ruff limpo; pytest 153 passed (nada existente quebrou).

Arquivo 2/3 — routers/activities.py completo. + from datetime import date. Rota GET /export entre GET "" e GET /{activity_id}. Validação: Select-String (confirmou date, export_activities_bulk, from_, to_, chamada ao service); ruff limpo; pytest 153 passed. Confirmação de ordem com Select-String "^async def |^@router\.(get|post|delete)" — export_activities_bulk antes de get_activity. ✅

Arquivo 3/3 — tests/test_export_bulk.py (novo). 11 testes. Validação: Select-String (11 funções); ruff check . limpo; pytest -q → 164 passed (153 + 11).
3.8 Fase 4 — validação em produção (com falso alarme diagnosticado)

Commit + push: 6cce475 feat(activities): export em lote CSV/GPX em ZIP (Sessao 22) (3 files, 628 insertions, create mode 100644 backend/tests/test_export_bulk.py). Push OK (ad7b99a..6cce475).

Primeira tentativa de validação (bloco grande): /activities/export?format=csv → 422. GPX → 422. format=xpto → 422. from>to → 422. from=2099-01-01 → 422. Quase abri diagnóstico de bug.

Diagnóstico correto: o padrão (todos 422, inclusive format=csv sem filtro) era exatamente o que acontece quando /export é capturado por /{activity_id} e "export" não é UUID. Mas o openapi.json mostrou /activities/export no ar e na ordem certa → causa real: o Render ainda não tinha terminado o redeploy quando o primeiro bloco rodou. A primeira tentativa foi prematura.

Segunda tentativa (baseline isolada): /activities/export?format=csv → 200. ?from=2099-01-01 → 200. ?to=2099-01-01 → 200. Confirmado: deploy tinha terminado entre as duas rodadas.

Validação completa (bloco Test-Bulk):
Check	Resultado
CSV default	200 application/zip, filename="rumo_export_20261108-204455.zip", 6 entries (nomes rumo_<id>_walk.csv)
GPX default	200 application/zip, filename="rumo_export_20261108-204456.zip", 6 entries (nomes rumo_<id>_walk.gpx)
from=2099-01-01	200, 0 entries
format=xpto	422
from>to	422

Todos os casos do contrato bateram. Backend S22 100% validado em produção.
3.9 Tropeços e correções (S22)

Tropeço 1 — falso alarme de 422 em produção. Causei estresse desnecessário ao rodar validação em produção imediatamente após git push, sem aguardar o redeploy do Render. Corrigido quando o openapi.json mostrou a rota no ar. Regra S22 nova: validar openapi.json antes de acusar bug em rota nova; aguardar redeploy.

Tropeço 2 — bloco de validação sem try/catch por chamada. Quando o primeiro Invoke-WebRequest estourou (422), o $r ficou $null e o resto do bloco cascateou erros feios (NullArray, WriteAllBytes bytes nulo, OpenRead arquivo não existe). Corrigido na segunda rodada com função Test-Bulk que captura o body de cada erro. Lição: blocos de validação em PowerShell devem ter try/catch por chamada e imprimir o BODY do erro — não deixar o PowerShell cuspir erros encadeados.

Tropeço 3 — Invoke-WebRequest sem -UseBasicParsing. Prompt de segurança do IE Engine. Usuário respondeu a (Sim para Todos) e funcionou. Regra S22 nova: sempre -UseBasicParsing.
3.10 Resultado da suíte

pytest -q → 164 passed (153 + 11 novos). ruff check . → All checks passed. npm run build → 824 modules verde (front não tocado). npm run lint → limpo. flutter analyze → No issues.
3.11 Commits pushados

    ad7b99a docs: handoff da Sessao 21 (pendência herdada; 342 insertions, 365 deletions).

    6cce475 feat(activities): export em lote CSV/GPX em ZIP (Sessao 22) (3 files, 628 insertions, create mode 100644 backend/tests/test_export_bulk.py).

Pendente: docs: handoff da Sessao 22 (este arquivo).
3.12 Validação em produção (backend)

Render redeployou após 6cce475. /activities/export validado (CSV→ZIP 6 entries, GPX→ZIP 6 entries, from futuro→ZIP vazio 0 entries, xpto→422, from>to→422). Front não mudou na S22 — nenhum redeploy novo na Vercel.
SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES
GET /activities/{id}/track (auth: Bearer JWT)

Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota".

Resposta (TrackResponse):
json

{
  "activity_id": "uuid",
  "type": "LineString",
  "coordinates": [[lon, lat], ...],
  "bbox": [minLon, minLat, maxLon, maxLat],
  "n_points": 60,
  "simplified": false
}

ActivityResponse (feed/lista/detalhe/busca)
json

{ ..., "bbox": [minLon, minLat, maxLon, maxLat] | null }

Ordem GeoJSON. null quando route IS NULL. Sem N+1.
GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21

    Permissão: dono OU seguidor do dono. Caso contrário, 404 ("Atividade não encontrada" — não vaza existência).

    format=csv (default): 200, Content-Type: text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.csv". 1 header + 1 linha. Funciona com ou sem rota (bbox_* vazios se sem rota). None → string vazia. lineterminator="\n". Colunas:
    id, activity_type, title, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, bbox_min_lon, bbox_min_lat, bbox_max_lon, bbox_max_lat

    format=gpx: 200, Content-Type: application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.gpx". <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…"> por ponto. Inverte [lon, lat] (GeoJSON) → lat/lon no atributo. Exige rota → 404 "Atividade não possui rota" se route IS NULL.

    format inválido → 422 (Literal do Pydantic).

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — NOVO na S22

    Auth: self-only. Exporta apenas as atividades do usuário autenticado. Não exporta atividades de terceiros, mesmo seguidos. Escopo "meus dados".

    Saída: ZIP (Content-Type: application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos, cada um no formato unitário.

    format=csv (default): ZIP com N .csv, cada um rumo_<id>_<type>.csv (1 header + 1 linha, bbox_* preenchidos se rota). Inclui todas as atividades do filtro (com ou sem rota).

    format=gpx: ZIP com N .gpx, cada um rumo_<id>_<type>.gpx. Só atividades com rota — as sem rota são omitidas (não gera GPX vazio).

    Filtro from/to (YYYY-MM-DD, UTC, inclusivo nas duas pontas):

        from: started_at >= from 00:00 UTC.

        to: started_at < (to + 1 dia) 00:00 UTC — inclui o dia inteiro.

        Sem from nem to → todas as atividades.

    Casos de borda:

        0 atividades no filtro → 200 com ZIP vazio (0 entries). Não é erro.

        from > to → 422 ("from deve ser <= to").

        format inválido → 422 (Literal).

        from/to em formato inválido → 422 (Pydantic date).

GET /activities/stats/summary?activity_type=<opcional>

→ StatsSummary: total_activities, total_distance_m, total_duration_s, total_elevation_gain_m, total_calories, avg_pace_s_per_km, avg_speed_mps.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional>

→ StatsWeeklyResponse: { weeks, items: [StatsPeriod] }. StatsPeriod: period_start (segunda), total_activities, total_distance_m, total_duration_s, total_calories.
GET /activities/stats/monthly?months=N&activity_type=<opcional>

→ StatsMonthlyResponse: mesmo shape, chave months, period_start "YYYY-MM-01".
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy>

→ StatsByTypeResponse: { items: [StatsByTypeItem] }. StatsByTypeItem: activity_type, total_activities, total_distance_m, total_duration_s, total_elevation_gain_m, total_calories, previous: StatsByTypePreviousItem | null. Só tipos com ≥1 atividade na janela atual. Ordenação: total_activities DESC, activity_type ASC (Python — enum nativo ordena pela ordem de declaração). period inválido → 422. compare inválido → 422. previous null para period="all" ou tipo ausente na janela.

Janelas:
period	compare	janela
all	qualquer	null
90d	prev (default)	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide — documentado em teste)
GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}

Mesmos shapes. by-type aceita period + compare. Permissão (_ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403 ("Você precisa seguir este usuário pra ver as estatísticas dele"); target inexistente → 404 ("Usuário não encontrado").
GET /auth/me — identidade do usuário logado (NÃO é /users/me)

Resposta: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }.
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9 a 21 commitadas e pushadas. origin/main == main == HEAD == 6cce475.

Sessão 22: backend commitado (6cce475). Falta commitar este handoff.

Primeira ação da S23:
powershell

cd D:\Rumo
git status --short
# Esperado: M docs/HANDOFF.md (o handoff da S22)
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 22"
git push
git --no-pager log --oneline -4
git status --short

Esperado depois: HEAD == origin/main com docs: handoff da Sessao 22 no topo, working tree limpo.

Nenhuma outra pendência conhecida de git.

Front "Exportar tudo" fica para S23 (primeira tarefa de código da próxima sessão — ver Seção 8).
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 23 — primeira ação] Abrir PowerShell via Win+R → powershell

NÃO abrir de dentro do VS Code / Windows Terminal. Depois:
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

[Sessão 23 — primeira ação] Commitar handoff S22 (se ainda não foi)
powershell

cd D:\Rumo
git status --short
# Esperado: M docs/HANDOFF.md
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 22"
git push
git --no-pager log --oneline -4
git status --short

[Sessão 23 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 23 — primeira ação] Docker + pytest local
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"      # ATENÇÃO: -a, não só ps
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
# Se o prompt já mostra (venv), PULE a linha abaixo.
.\venv\Scripts\Activate.ps1      # UM ponto, NÃO dois
python -m pytest -q              # esperado: 164 passed
ruff check .

[Sessão 23 — primeira ação] Detecção de versão em produção (S22 — export em lote)

⚠️ Sempre -UseBasicParsing (evita prompt). ⚠️ Depois de git push, aguardar redeploy do Render antes de validar.
powershell

# Passo 1: confirmar que a rota nova está no openapi.json
$openapi = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json"
$hasBulkExport = $openapi.paths.PSObject.Properties.Name -contains "/activities/export"
Write-Host "rota /activities/export no ar: $hasBulkExport"
if (-not $hasBulkExport) {
  Write-Host "RENDER AINDA NAO REDEPLOYOU. Aguardar 1-3 min ou Manual Deploy no dashboard."
}

# Passo 2: detecção de versão
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }

Add-Type -AssemblyName System.IO.Compression.FileSystem
$tmp = [System.IO.Path]::GetTempFileName()

try {
  $r = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/export?format=csv" -Headers $h -UseBasicParsing
  Write-Host "CSV default: $($r.StatusCode) $($r.Headers['Content-Type'])"
  [System.IO.File]::WriteAllBytes($tmp, $r.Content)
  $zip = [System.IO.Compression.ZipFile]::OpenRead($tmp)
  Write-Host "  entries: $($zip.Entries.Count)"
  $zip.Dispose()
} catch {
  $resp = $_.Exception.Response
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
  Write-Host "CSV FALHOU: $($resp.StatusCode.value__) - $($reader.ReadToEnd())"
}

# Se CSV deu 200 + application/zip com entries > 0, backend está na S22.

Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id

Stats de terceiros (S19/S20)
powershell

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d&compare=yoy" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

Ruff (backend)
powershell

cd D:\Rumo\backend
# Se o prompt já mostra (venv), pule:
.\venv\Scripts\Activate.ps1
ruff check .

Recuperação de arquivo corrompido (lição S21)
powershell

cd D:\Rumo
git status --short <arquivo>                                   # "M" se modificado, vazio se igual ao HEAD
git --no-pager log --oneline -3 -- <arquivo>                    # último commit que tocou
# Se o último commit for anterior à mudança quebrada:
git restore <arquivo>                                          # ou git checkout -- <arquivo>
# Se a versão quebrada JÁ foi commitada:
git show <commit-anterior>:<arquivo> > <arquivo>
# Conferir que voltou:
Get-Content -Encoding UTF8 <arquivo> | Select-String -Pattern "async def "

Diagnóstico: rota nova não responde após git push (lição S22)
powershell

# 1) openapi.json — a rota está no ar?
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"
# Se vazio: Render não redeployou. Aguardar ou Manual Deploy no dashboard.
# 2) se a rota está no ar mas retorna 422, ver o BODY do erro:
try {
  Invoke-WebRequest -Uri "<url>" -Headers $h -UseBasicParsing | Out-Null
} catch {
  $resp = $_.Exception.Response
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
  Write-Host "STATUS $($resp.StatusCode.value__): $($reader.ReadToEnd())"
}

SEÇÃO 7 — DÍVIDAS TÉCNICAS

    (FECHADA na S20) ~~Existem duas pastas de venv~~: .venv (fantasma) removida. Única venv é backend\venv (Python 3.13.7).

    (FECHADA na S20) ~~Pylance reclamando de imports~~: .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"].

    (CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type faz desempate em Python: items.sort(key=lambda r: (-r["total_activities"], r["activity_type"])). Qualquer novo ORDER BY em coluna Enum DEVE (a) fazer o sort final em Python, ou (b) ser testado contra a ordem de declaração.

    (CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes de period DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias. Não misturar com _dt fixo.

    (CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN. Quando um SELECT soma duas janelas, o WHERE deve cobrir a união. Cada métrica recorta via SUM(CASE WHEN <janela> THEN col ELSE 0 END).

    (CONHECIDA — Sessão 17/18/19/20/21/22) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. O segmented control de período afeta APENAS a tabela por tipo. Intencional.

    (CONHECIDA — Sessão 17/18/19/20/22) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. Isso NÃO é bug. Os 164 testes locais provam filtro e previous.

    (CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática. Documentado em teste. Não é bug.

    (CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — o <type> interno traduz para "walk" via map_gpx_type. Os testes de export usam activity.activity_type.value dinâmico em vez de hardcodar. Se trocar o sample, os testes continuam passando.

    (CONHECIDA — Sessão 21) to_gpx não emite <time> por <trkpt> (a geometria guardada em route é só LineString, sem stream temporal — decisão da S10). O <trk> tem <name> e <type>, mas os pontos não têm timestamp individual. Strava/Garmin aceitam GPX assim. Se "export com timestamps" virar requisito, precisa ler raw_track_points em vez de route — mudança pontual em to_gpx + assinatura.

    (CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. Não há caso de uso hoje (todo export exige auth). Adicionar quando aparecer (YAGNI).

    (CONHECIDA — Sessão 22) export_activities_bulk faz O(N) queries (get_activity por atividade + get_activity_track por atividade com rota no GPX). Aceitável para export raro. Se virar gargalo, otimizar com SELECT único + bbox por linha — mas aí duplica a lógica de _attach_counts. Preferi reusar.

    (CONHECIDA — Sessão 22) Export em lote é self-only. Se o produto quiser "exportar atividades de quem eu sigo", precisa mudar _get_user_activity_ids_in_range para aceitar user_id de terceiros + checar follow em _ensure_can_view_stats (ou equivalente). Decisão de privacidade, não é bug.

    (Oportunidade — S18/S19/S20/S21/S22) Delta "vs. anterior / vs. ano anterior" cobre 3 métricas (atividades, distância, elevação). Tempo e calorias ficaram fora por legibilidade. Extensão trivial se virar requisito.

    (Oportunidade — S18/S19/S20) Semântica do delta é NEUTRA (subiu=verde, desceu=vermelho, igual=cinza). Sem juízo de "melhor/pior". Se o produto quiser meta, é feature nova.

    (Oportunidade — S19/S20) Stats públicas só aparecem quando viewer segue o alvo. "Stats públicas sempre" é mudança de regra em _ensure_can_view_stats (endpoint + teste + front). Não é bug — é decisão de privacidade documentada.

    (Oportunidade) RouteMap.tsx é reutilizável. Se aparecer segundo uso, considerar React.lazy() para tirar o leaflet (163.60 kB) do chunk.

    (Oportunidade — S21/S22) Export com timestamps por ponto — ver dívida da S21 acima.

    (Oportunidade — S22) Export em lote no app mobile (mesma feature do web). Mobile está parado desde S11; seria sessão grande.

    (Oportunidade — S22) Export em lote concatenado (1 CSV com todas as atividades + 1 GPX com todos os tracks). Decidimos ZIP na S22 (motivos no contrato). Se o produto quiser "1 arquivo grande", é feature paralela.

Mobile: sem drill-down de stats. Sem inclinação/rotação 3D. Sem export. TimeoutException do app mobile não reproduzido desde a Sessão 9.
SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 23 e além)
PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 23 (antes de qualquer mudança de código)

No terminal (PowerShell via Win+R → powershell):
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

Esperado: git push "Everything up-to-date"; HEAD == origin/main == docs: handoff da Sessao 22 (se já commitado) ou 6cce475 (se o handoff ainda não foi commitado); git status --short vazio ou com M docs/HANDOFF.md.

Se as 3 linhas M aparecerem: commitar o handoff (Seção 6). Depois, sanidade de build:
powershell

cd D:\Rumo\web ; npm run build ; npm run lint
cd ..\mobile ; & "C:\Users\nasci\flutter\bin\flutter.bat" analyze

Depois, Docker + pytest (com docker ps -a, não só ps):
powershell

docker version ; docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
# Se prompt já mostra (venv), pular:
.\venv\Scripts\Activate.ps1
python -m pytest -q     # esperado: 164 passed
ruff check .

Depois, detecção de versão em produção (S22 — export em lote; Seção 6, bloco "Detecção de versão em produção (S22)"). Esperado: openapi.json com /activities/export, CSV→ZIP 200 com ≥1 entry.
Estado da Rota B (fim da Sessão 22)

Cinco itens fechados: filtro de período (S17), comparação com janela anterior (S18), stats públicas em perfis de terceiros (S19), year-over-year (S20), export unitário CSV/GPX (S21), export em lote CSV/GPX em ZIP (S22). A Rota B "original" está concluída e o backend está bem servido.
Próximos passos (escolha entre opções)

OPÇÃO 1 — Front "Exportar tudo" (paridade com backend S22). ← RECOMENDADA

    Consumir o endpoint GET /activities/export na UI. Botão "Exportar tudo" em ProfilePage (recomendação — é onde o usuário vê "minhas atividades" e o resumo; dropdown CSV/GPX + date range opcional). Alternativa: ActivitiesPage.

    Backend 100% pronto. Front só consome.

    Escopo: ~30–45 min, 3 arquivos (web/src/api/activities.ts adicionar downloadActivityExportBulk, web/src/pages/ProfilePage.tsx com botão + estado, web/src/api/client.ts se apiFetchBlob não cobrir).

    Motivos: feature visível ao usuário, fechamento natural da S22, testável em build/lint sem depender de backend novo, escopo pequeno.

OPÇÃO 2 — Export no app mobile (paridade com web).

    Mobile parado desde S11. Sessão grande. Só se houver demanda real.

    Não recomendo para S23 — sessão grande, alto risco, e o app mobile tem outras lacunas (sem stats drill-down, sem share).

OPÇÃO 3 — Resíduos de baixo risco (Rota A+).

    (a) RouteMap com React.lazy() — prepara para segundo uso. ~30 min.

    (b) Cheat sheet de endpoints num README.md. ~30 min.

    Ganho marginal. Só se não houver Rota B clara.

OPÇÃO 4 — Export com timestamps por ponto.

    Muda to_gpx para ler raw_track_points (que tem [[lat, lon, ele, ts], ...]) em vez de route. Mantém route para o mapa; export lê raw_track_points.

    Feature de nicho (Strava/Garmin aceitam GPX sem <time>, mas apps de análise preferem com). Custa pouco, mas não é prioridade.

OPÇÃO 5 — Export em lote no mobile (paridade) ou "exportar tudo" via app.

    Combina com Opção 1 + Opção 2. Só depois de decidir se o mobile vai evoluir.

Recomendação final para a Sessão 23

Antes de escolher, VALIDAR ESTADO (Seção 8 — primeira ação). Se tudo verde (build, lint, analyze, pytest 164, /activities/export respondendo em prod), aí escolher.

Rota recomendada: OPÇÃO 1 (front "Exportar tudo").

Motivos:

    Backend S22 entregue e validado; o front é o que falta para o usuário usar a feature.

    Escopo pequeno (~30–45 min).

    Fecha a feature de export (unitário S21 + em lote S22) do lado do produto.

    Testável em npm run build + npm run lint sem depender de backend novo.

Se preferir escopo menor: OPÇÃO 3 (React.lazy no RouteMap + README).

Se preferir escopo maior: OPÇÃO 2 (mobile) — mas avisar antes que é sessão grande.

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 23 neste mesmo formato (seções 0 a 9).
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22, o usuário reforçou: "sempre vamos seguir o que você recomendar" e "vamos sempre fazer o que você recomendar".

Pedido para o assistente da S23 (e além): manter o processo da S21/S22. Concretamente:

    Fase 0 obrigatória: validar estado (git, build, lint, analyze, docker -a, pytest, detecção de versão em prod) antes de tocar em qualquer código.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. Pedir também models/activity.py, models/follow.py quando a feature tocar esses models.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — regra S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (front) entre cada entrega. Nunca acumular 2 arquivos sem validar.

    Fase 4 — validação em produção: local verde é pré-requisito; prod via HTTP/browser é o que fecha. Depois de git push, checar openapi.json antes de acusar bug (regra S22).

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir.

Regras novas da S21 (Seção 0, itens 7, 8, 9) e S22 (itens 10, 11): nunca placeholder no código; não adivinhar nomes de símbolos; git status + git log antes de git restore; Invoke-WebRequest sempre com -UseBasicParsing; validar openapi.json antes de acusar bug em rota nova.

O que funcionou nas S21/S22 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros (placeholder, _client_as sem get_db, os 3 nomes errados na S21; falso alarme de 422 na S22) e correção com base no output real do terminal, não na previsão.