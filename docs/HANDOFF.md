HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 21
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação sobre o projeto chega por DUAS vias:

(a) o usuário cola o conteúdo de um arquivo com Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal

NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere o usuário colar. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

Sessões anteriores perderam tempo porque o assistente tentou "adivinhar" a árvore de diretórios e errou. Não repetir.
⚠️ REGRA NOVA DA SESSÃO 21 — nunca placeholder no código entregue

A S21 teve dois tropeços causados pela mesma causa raiz: eu entreguei um bloco de código com o marcador # ... (resto do arquivo INALTERADO ...) ... como "rascunho didático". O usuário colou no activity_service.py (arquivo grande, com get_activity/get_activity_track/create_activity/etc.) e sobrescreveu o arquivo inteiro — o placeholder virou o arquivo real, e todas as funções-base sumiram. Recuperado com git restore (o arquivo não tinha sido commitado; git log confirmou que o último commit que o tocou foi b8e4084, da S10).

Regra permanente: quando eu não tiver o conteúdo de um arquivo existente, NÃO entrego nem "rascunho de bloco". Peço o arquivo (Get-Content -Encoding UTF8) e só entrego completo, pronto para Ctrl+A → colar → salvar. Nunca marcador no meio do código, mesmo com aviso em negrito. É o único jeito de eliminar esse tipo de erro.
Regra nova — não adivinhar nomes de símbolos do projeto

No test_export.py, eu escrevi ActivityType.run (era ActivityType.RUN) e Follow(followed_id=...) (era following_id=...). O ruff não pega (é semântico, não sintático) — só o pytest pegou, com tracebacks claros. Custou 1 ida e volta para pegar o follow.py e outro para corrigir o teste.

Regra permanente: antes de escrever teste ou código que referencia símbolo de model/enum/schema do projeto, peça o arquivo (models/activity.py, models/follow.py, schemas/activity.py, etc.). É barato (são pequenos) e elimina a classe de erro. Se o arquivo for grande, peça só as primeiras N linhas (Select-Object -First 100) — o suficiente para ver a assinatura.
Regra nova — git status antes de qualquer git restore/git checkout

Sempre rodar git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo> antes de tentar restaurar. Se o último commit que tocou o arquivo for anterior à mudança quebrada, git checkout/git restore restaura. Se a versão quebrada já foi commitada, git show <commit-anterior>:<caminho> > <caminho> é o caminho.
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos — o usuário precisa colar conteúdo e saídas de terminal.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app). Backend de produção usa Postgres/PostGIS gerenciado. Testar via HTTP é sempre possível.

IMPORTANTE — usuário NÃO tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam automaticamente, validar via HTTP em produção. Não presumir que o usuário vai "rodar o app localmente" para testar UI.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (153 passed ao fim da Sessão 21 — 143 + 10 novos do export). Container de teste rumo_postgres_test na porta 5433.

ATENÇÃO — docker ps sozinho esconde container parado. Na abertura da S21, pytest -q falhou com 126 erros de ConnectionRefusedError: [WinError 1225] porque o container rumo_postgres_test estava Exited (255) (Docker Desktop encerrou/reiniciou entre S20 e S21). O docker ps -a --filter "name=rumo_postgres_test" mostrou Exited; up -d subiu; pg_isready respondeu accepting connections; pytest voltou a 143. Primeira verificação da S22+ deve ser docker ps -a --filter "name=rumo_postgres_test" (com -a), não só docker ps.

Para reativar numa sessão nova:

    Abrir Docker Desktop e esperar a baleia verde.

    Garantir que o terminal foi aberto via Win+R (fora do VS Code / Windows Terminal, que herdam PATH antigo).

    cd D:\Rumo\backend

    docker compose -f docker-compose.test.yml up -d

    docker ps -a --filter "name=rumo_postgres_test" (deve mostrar Up … (healthy))

    docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432 (deve dizer accepting connections)

    .\venv\Scripts\Activate.ps1 (UM ponto, não dois)

    python -m pytest -q

VENV: ao fim da S21, a única venv é D:\Rumo\backend\venv (sem ponto), Python 3.13.7. A .venv antiga (fantasma) foi removida na S20. .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"].

ATENÇÃO: py -3 deste Windows aponta para Python 3.14 (incompatível com requirements.txt). Se precisar recriar a venv: py -3.13 -m venv D:\Rumo\backend\venv ou C:\Python313\python.exe -m venv D:\Rumo\backend\venv.
Estrutura do repo (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada na Sessão 19 e inalterada em estrutura na S20/S21 (só arquivos modificados/criados, nenhum removido):
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
│   │                              # test_export.py (NOVO na S21) + test_follow.py +
│   │                              # test_like.py + test_stats.py + __init__.py
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

⚠️ Lições S18/S19/S20/S21 — detecção de versão no ar:

    422 de versão NÃO distingue S17 de S18. /activities/stats/by-type?period=30d devolve 422 desde a S17.

    Para S19: GET /users/{meId}/stats/summary responde 200 (não 404) e GET /users/me responde 422.

    Para S20: GET /activities/stats/by-type?period=90d&compare=yoy responde 200. E ?compare=xpto responde 422.

    Para S21: GET /activities/{id}/export?format=csv e ?format=gpx respondem 200; ?format=xpto responde 422. Se der 404 em format=csv num id válido, o backend ainda está na S20.

⚠️ Lição S20/S21 — previous: null em prod/Prod2 não é bug. Nenhuma das contas de teste tem atividade na janela de comparação. Os 143/153 testes locais provam que a janela funciona.
O que o assistente precisa pedir ao usuário (não tem acesso a arquivos)

    Conteúdo de arquivos via Get-Content -Encoding UTF8 <caminho>. SEMPRE passar -Encoding UTF8; sem isso, acentos viram inÃ­cio.

    Saídas de comandos (flutter analyze, npm run build, git log, git status, pytest -q, ruff check).

    Nunca assumir estrutura "de cabeça": pedir o arquivo antes de reescrevê-lo.

ATENÇÃO — arquivos truncados/duplicados: se um Get-Content vier com a última linha cortada OU com o conteúdo DUPLICADO, NÃO adivinhar o final. Pedir ruff check <arquivo> (lista duplicatas de uma vez) e entregar o arquivo completo para Ctrl+A → colar → salvar.

ATENÇÃO — arquivo "salvo" que não salvou. SINTOMA: build ou pytest falha dizendo que um símbolo novo não existe, mesmo o assistente tendo entregado o arquivo. DIAGNÓSTICO: Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>". Se não aparecer, o disco ainda é o antigo. REGRA: depois de entregar um arquivo que muda contrato, pedir a confirmação com Get-Content | Select-String ANTES de rodar build/test.

ATENÇÃO — git diff pipeado no PowerShell pode exibir acentos como mojibake. Artefato de codepage do pipe, NÃO corrupção.

ATENÇÃO — git log --oneline no PowerShell às vezes cola a última linha com o prompt. Formatação, não corrupção.

ATENÇÃO — git log sem --no-pager abre o less e trava o terminal. SEMPRE usar git --no-pager log ... ou prefixar com $env:PAGER="".

ATENÇÃO — Pylance reclamando de imports (fastapi/sqlalchemy/pytest) NÃO é erro de código. Interpretador errado. Causa raiz corrigida na S20: .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"]. Se voltar: Ctrl+Shift+P → "Python: Select Interpreter" → D:\Rumo\backend\venv\Scripts\python.exe → Developer: Reload Window.

ATENÇÃO — save confirmado via Select-String (lição S20/S21): prever "esperado vazio" ou "esperado 0 ocorrências" em checks de validação é fonte de falso alarme. Priorizar SEMPRE o output real do terminal em vez da expectativa do assistente. Quando o output divergir da previsão, investigar o output primeiro.
Acordos de trabalho (válidos em todas as sessões — REFORÇADOS na S21)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário. (Usuário reforçou isso nas S15–S21.) O assistente decide e recomenda; não fica perguntando "qual opção você prefere?".

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder no meio do código. Preservar imports, comentários e trechos que já funcionam. Destacar o trecho alterado com comentário curto acima (// [Sessão N] ou // [Sessão N — fix]).

    UMA versão por arquivo por resposta. Se errar no meio do raciocínio, cortar a versão errada e entregar só a corrigida com nota de 1 linha. NUNCA duas versões do mesmo arquivo na mesma resposta.

    HANDOFF PREVENTIVO em ~70-80% do limite de contexto: parar o trabalho em curso e entregar o HANDOFF completo neste mesmo formato (seções 0 a 8), pronto para colar no próximo chat. Deve ser COMPLETO e bem explicado, não resumido.

    VALIDAÇÃO INCREMENTAL: quando a mudança toca mais de um arquivo da mesma stack, colar o(s) arquivo(s) base e rodar build/analyze antes de entregar o próximo — reduz superfície de erro. Exceção legítima: 2 arquivos acoplados por mudança de contrato interno (ex.: hook + consumidor do hook). Nesse caso, entregar os 2 juntos e rodar 1 build.

    VERIFICAR SAVE ANTES DE BUILD: quando o assistente entrega um arquivo com símbolo novo (tipo, função, param), pedir ao usuário Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>" antes de rodar build/test.

    (NOVA S21) NUNCA placeholder no código entregue. Se o assistente não tem o conteúdo de um arquivo existente, peça e espere — não entregue "rascunho de bloco". Violar essa regra quebrou o activity_service.py (recuperado com git restore).

    (NOVA S21) Não adivinhar nomes de símbolos. Antes de referenciar ActivityType.X, Follow(...), campos de schema, etc., peça o arquivo do model/enum/schema. ruff não pega, pytest pega com traceback claro — mas custa ida e volta.

    (NOVA S21) Antes de git restore/git checkout, rodar git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>. Confirmar que o último commit que tocou o arquivo é anterior à mudança quebrada.

Processo que o usuário elogiou na S21 (para manter)

O usuário disse textualmente: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho." O que funcionou:

    Ordem clara: Fase 0 (validação de estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 4 (validação em produção) → Fase 5 (handoff).

    Descoberta antes de codar: pedir gpx_service.py, routers/activities.py, schemas/activity.py, tests/conftest.py, test_stats.py (primeiras 80 linhas), requirements.txt, web/api/activities.ts, web/pages/ActivityDetailPage.tsx, web/api/client.ts, models/activity.py, models/follow.py. Cada pedido com motivo.

    Validação entre cada entrega: Select-String (save) + ruff + pytest no backend; npm run build + npm run lint no front. Nunca acumular 2 arquivos sem validar.

    Contrato travado escrito antes de codar: endpoint, auth, 404 vs 422, headers, formato CSV/GPX. O usuário leu e aprovou tacitamente ("sempre seguir recomendação").

    Commits pequenos e temáticos: docs: handoff da Sessao 20, feat(activities): export CSV/GPX (Sessao 21), feat(web): botoes baixar CSV/GPX no detalhe (Sessao 21).

    Validação em produção separada da local: local verde é pré-requisito, mas prod via HTTP/browser é o que fecha.

Pedido explícito do usuário para o próximo chat: "se tiver como pedir para que sempre trabalhe desta forma". Manter o processo acima em todas as sessões.
SEÇÃO 1 — TL;DR para quem chega agora

Backend: 153 testes passando LOCALMENTE (pytest -q verde na Sessão 21 — 143 + 10 novos do export), 0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon,minLat,maxLon,maxLat], n_points, simplified. 404 quando route é NULL.

ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax do PostGIS no mesmo SELECT (sem N+1). None quando route é NULL.

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.

Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (helper _ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

NOVO na S21 — Export:

    GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor (mesma regra do /track; senão 404). Retorna Response com Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>".

        CSV: text/csv; charset=utf-8, 1 header + 1 linha. Colunas: id, activity_type, title, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, bbox_min_lon, bbox_min_lat, bbox_max_lon, bbox_max_lat. None → string vazia. bbox_* vazios quando route IS NULL. lineterminator="\n" (não \r\n). CSV funciona sem rota.

        GPX: application/gpx+xml; charset=utf-8, <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…">. Exige route IS NOT NULL (404 "Atividade não possui rota", consistente com /track). coordinates vêm em ordem GeoJSON [lon, lat] e são invertidos para lat/lon no atributo. format inválido → 422 (Literal do Pydantic). format omitido → default csv.

Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet (RouteMap no detalhe) + recharts (gráficos no perfil). Drill-down por tipo tem segmented control de janela temporal (S17), coluna "vs. anterior" com delta colorido (S18), 2º segmented control "Comparar com:" (prev/yoy) que só aparece quando period !== "all" (S20). S21: botões "Baixar CSV" (sempre) e "Baixar GPX" (condicional a track) no cabeçalho do ActivityDetailPage. Helper apiFetchBlob em client.ts (aditivo, não mexe no apiFetch). downloadActivityExport(id, format) em activities.ts.

Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite), alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds. Intocado desde a S11. Sem drill-down de stats no app. Sem export no app.
Entregas da Sessão 21

Backend — export CSV/GPX:

    gpx_service.py: + to_gpx(activity, coordinates) -> str (usa gpxpy.gpx.GPX() + GPXTrackPoint). Só parse existia; agora tem geração também. Import novo: import gpxpy.gpx.

    activity_service.py: + bloco # ===== Export (CSV / GPX) — [Sessão 21] ===== no fim: _CSV_COLUMNS, _activity_type_str, _activity_to_csv, _export_filename, export_activity(db, viewer_id, activity_id, fmt) -> tuple[bytes, str, str]. Reusa get_activity (CSV) e get_activity_track (GPX) — herda auth dono-ou-seguidor sem reimplementar. import csv, import io, from typing import Literal (topo). to_gpx adicionado ao import de gpx_service (já existente: map_gpx_type, parse_gpx).

    routers/activities.py: + Response no import do FastAPI; + rota GET /{activity_id}/export entre /track e DELETE /{activity_id}. Response(content=body, media_type=content_type, headers={"Content-Disposition": ...}).

    tests/test_export.py (NOVO): 10 testes:

        test_export_csv_owner_ok — 200, text/csv, Content-Disposition correto, header + 1 linha, valores batem.

        test_export_csv_no_route_owner_ok — funciona sem rota; bbox_* vazios.

        test_export_csv_nonexistent_activity_404.

        test_export_csv_not_follower_404.

        test_export_csv_follower_ok (usa Follow(follower_id=..., following_id=...) — não followed_id, ver lição S21).

        test_export_gpx_owner_ok — 200, application/gpx+xml, <trkpt> reparseado via gpxpy.parse, compara lat/lon com activity.raw_track_points[i] (pytest.approx(abs=1e-6)) → prova a inversão [lon,lat]→lat/lon.

        test_export_gpx_no_route_404 (checa "rota" no detail).

        test_export_gpx_not_follower_404.

        test_export_invalid_format_422.

        test_export_default_format_is_csv (sem ?format → csv).

        Helper _client_as(user, test_engine): sobrescreve get_db E get_current_user (a v1 só sobrescrevia get_current_user e o _client_as tentaria conectar no Postgres de produção — corrigido antes de commitar).

        Assert de filename é dinâmico: activity.activity_type.value, não "run" hardcoded (o sample_run.gpx tem <type> que o map_gpx_type traduz para "walk" — nome do arquivo engana).

Front — botões de download:

    client.ts: + BlobResult, _parseContentDispositionFilename(header), apiFetchBlob(path, options?). Espelha auth/erro do apiFetch mas usa res.blob(). 401 limpa token. Content-Disposition é parseado com regex /filename="?([^";]+)"?/i. Não modifica apiFetch (caminho quente JSON fica intocado).

    activities.ts: + ActivityExportFormat = "csv" | "gpx", _triggerDownload(blob, filename) (privado, URL.createObjectURL + <a download> + revokeObjectURL em setTimeout(0)), downloadActivityExport(id, format) (usa apiFetchBlob, fallback rumo_<id>.<format> se o header faltar).

    ActivityDetailPage.tsx: + import { useState } (não tinha — o componente usava só hooks do TanStack), + import { downloadActivityExport }, + const [busyCsv, setBusyCsv], + const [busyGpx, setBusyGpx], + handleDownload(format) com try/catch (ApiError.detail → alert), + const hasTrack = !!track && track.coordinates.length > 0, + o <h1> foi envolvido em <div className="flex items-start justify-between gap-2 flex-wrap"> com os botões à direita. CSV sempre visível; GPX condicional a hasTrack. Visível para dono E seguidor (backend aceita os dois).

Estado final da S21: working tree limpo. HEAD == origin/main == 8936415 (backend) — aguardando o commit do front (S21 termina sem ter commitado o front; ver Seção 5).

Render: /activities/{id}/export respondendo em produção (validado pelo usuário: "tudo como esperado").
Vercel: front deployado; validação visual no browser não foi colada nesta sessão — fica como primeira ação da S22 (ver Seção 8).
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

    Deps novas em S21: nenhuma (gpxpy==1.6.2 já estava em requirements.txt desde a S13 para o upload; reaproveitado no export).

Git (estado ao fim da Sessão 21)
text

8936415 (HEAD -> main, origin/main) feat(activities): export CSV/GPX (Sessao 21)
19ebc3b docs: handoff da Sessao 20
2ca4c81 feat(web): toggle year-over-year no drill-down por tipo (Sessao 20)
879d885 feat(stats): comparacao year-over-year no drill-down por tipo (Sessao 20)
09a6596 docs: handoff da Sessao 19
0df0b9f feat(web): stats no perfil de terceiros seguidos (Sessao 19)
229e36b feat(users): stats publicas em perfis de terceiros (Sessao 19)
4ba08da docs: handoff da Sessao 18
b0e3a29 feat(stats): comparacao com janela anterior no drill-down por tipo (Sessao 18)
494d8cc docs: handoff da Sessao 17
5925a03 feat(stats): filtro de periodo no drill-down por tipo (90d|1y|all)
0f1c6ef chore(web): remove bboxToOsmTileUrl deprecated da Sessao 16

⚠️ O commit do front da S21 NÃO foi feito ainda (o usuário validou o build local mas parou antes de commitar o feat(web): botoes baixar CSV/GPX no detalhe (Sessao 21)). Os 3 arquivos estão modificados no working tree:

    web/src/api/client.ts

    web/src/api/activities.ts

    web/src/pages/ActivityDetailPage.tsx

Primeira ação da S22 (ver Seção 8) inclui commitar isso.
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 21
3.1 Validação de estado inicial

PowerShell via Win+R. git push: Everything up-to-date. HEAD == origin/main == 2ca4c81 (S20). git status --short: só M docs/HANDOFF.md (handoff da S20 não commitado, herdado). npm run build: verde, 824 modules. flutter analyze: No issues. Docker/compose OK.

Primeiro pytest -q falhou com 126 erros de ConnectionRefusedError: [WinError 1225]. Causa: rumo_postgres_test estava Exited (255) (Docker Desktop encerrou entre S20 e S21). docker ps sozinho não mostrava. docker ps -a --filter "name=rumo_postgres_test" mostrou. up -d subiu. pg_isready OK. pytest -q → 143 passed. Lição incorporada na Seção 0.
3.2 Decisão de rota: Opção 2 (export CSV/GPX)

Escolhida na S20 como recomendação. Justificativa: evolução natural depois das stats (dados agregados → dados brutos), reaproveita gpxpy já em uso no upload, contrato aditivo puro, testável 100% local, cabe em 1 sessão de tamanho médio.
3.3 Contrato travado antes de codar

GET /activities/{activity_id}/export?format=csv|gpx. Auth dono-ou-seguidor (herdada). 404 para inexistente/sem permissão. 404 para gpx sem rota. 422 para format inválido. Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>". CSV com 15 colunas (1 header + 1 linha). GPX com <trk>/<trkseg>/<trkpt> invertendo [lon, lat] → lat/lon. Contrato escrito e apresentado ao usuário antes da 1ª linha de código.
3.4 Ordem de entrega (validada incrementalmente)

Backend: gpx_service.py → activity_service.py → routers/activities.py → tests/test_export.py (cada um com Select-String de save + ruff + pytest antes do próximo). Front: client.ts → activities.ts → ActivityDetailPage.tsx (cada um com Select-String + npm run build + npm run lint).
3.5 Tropeços e correções

Tropeço 1 — placeholder no activity_service.py (grave).
Entreguei o bloco de export com # ... (resto do arquivo INALTERADO ...) ... como marcador. O usuário colou no arquivo real e sobrescreveu tudo. Ruff/Pylance acusaram get_activity/get_activity_track undefined. Diagnóstico: o arquivo estava com o placeholder no disco; git status --short backend/app/services/activity_service.py vazio (não commitado), git log --oneline -3 -- ... mostrou que o último commit que o tocou era b8e4084 (S10). git restore backend/app/services/activity_service.py recuperou. Regra nova na Seção 0.

Tropeço 2 — _client_as sem get_db override.
Na v1 do test_export.py, _client_as(user) só sobrescrevia get_current_user. Resultado: usaria o get_db real (engine de produção) e os testes de permissão falhariam com erro de conexão. Corrigido para _client_as(user, test_engine) sobrescrevendo os dois (get_db com session nova por request usando test_engine, e get_current_user com o user do cenário).

Tropeço 3 — 3 nomes errados no test_export.py.

    ActivityType.run → ActivityType.RUN (o enum é RUN = "run", UPPER_CASE). Peguei no models/activity.py que o usuário colou.

    Follow(followed_id=...) → Follow(following_id=...) (model usa following_id, não followed_id). Peguei no models/follow.py que o usuário colou.

    rumo_<id>_run.csv hardcoded → rumo_<id>_<activity.activity_type.value>.csv dinâmico (o sample_run.gpx traduz para "walk", não "run" — nome do arquivo engana).
    Lição na Seção 0.

3.6 Resultado da suíte

pytest -q → 153 passed (143 + 10 novos). ruff check . → All checks passed. npm run build → 824 modules verde, ActivityDetailPage 13.00 kB (+0.99 kB vs. S20). npm run lint → limpo.
3.7 Commits pushados

    19ebc3b docs: handoff da Sessao 20 (pendência herdada; 688 inserções, 866 deleções).

    8936415 feat(activities): export CSV/GPX (Sessao 21) (4 files, 556 insertions, 4 deletions; create mode 100644 backend/tests/test_export.py).

O commit do front ficou pendente (build verde, mas o usuário parou aqui — ver Seção 5).
3.8 Validação em produção (backend)

Render redeployou após 8936415. Usuário confirmou: "tudo como esperado". /activities/{id}/export respondendo. (Não foi colada a saída crua dos curls nesta sessão, mas o usuário deu OK explícito.)

Front em produção (Vercel): deployado, mas validação visual no browser NÃO foi colada. Fica para a S22.
SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES
GET /activities/{id}/track (auth: Bearer JWT)

Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route is None → detail "Atividade não possui rota".

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

Ordem GeoJSON. Null quando route IS NULL. Sem N+1.
GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — NOVO na S21

    Permissão: dono OU seguidor do dono. Caso contrário, 404 ("Atividade não encontrada" — não vaza existência).

    format=csv (default): 200, Content-Type: text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.csv". 1 header + 1 linha. Funciona com ou sem rota (bbox vazio se sem rota). None → string vazia. lineterminator="\n". Colunas:
    id, activity_type, title, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, bbox_min_lon, bbox_min_lat, bbox_max_lon, bbox_max_lat

    format=gpx: 200, Content-Type: application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.gpx". <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…"> por ponto. Inverte [lon, lat] (GeoJSON) → lat/lon no atributo. Exige rota → 404 "Atividade não possui rota" se route IS NULL.

    format inválido → 422 (Literal do Pydantic).

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

Sessões 9 a 20 commitadas e pushadas. origin/main == main == HEAD == 8936415.

Sessão 21: backend commitado (8936415), front NÃO commitado — os 3 arquivos estão no working tree:
text

M web/src/api/client.ts
M web/src/api/activities.ts
M web/src/pages/ActivityDetailPage.tsx

Primeira ação da S22: commitar o front:
powershell

cd D:\Rumo
git add web/src/api/client.ts web/src/api/activities.ts web/src/pages/ActivityDetailPage.tsx
git commit -m "feat(web): botoes baixar CSV/GPX no detalhe (Sessao 21)"
git push

Sessão 21 também entrega este handoff (a commitar como docs: handoff da Sessao 21 — geralmente primeira ação da S22, junto com o commit do front).

Nenhuma outra pendência conhecida de git.
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 22 — primeira ação] Abrir PowerShell via Win+R → powershell

NÃO abrir de dentro do VS Code / Windows Terminal. Depois:
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

[Sessão 22 — primeira ação] Descobrir o estado do front pendente
powershell

cd D:\Rumo
git status --short
# Esperado: 3 linhas M em web/src/...
# Se estiver vazio, o front da S21 já foi commitado em outra sessão — conferir com git log.

# Commitar o front pendente (se ainda não foi):
git add web/src/api/client.ts web/src/api/activities.ts web/src/pages/ActivityDetailPage.tsx
git commit -m "feat(web): botoes baixar CSV/GPX no detalhe (Sessao 21)"
git push

[Sessão 22 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 22 — primeira ação] Docker + pytest local
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"      # ATENÇÃO: -a, não só ps
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
# Se o prompt já mostra (venv), PULE a linha abaixo.
.\venv\Scripts\Activate.ps1      # UM ponto, NÃO dois
python -m pytest -q              # esperado: 153 passed
ruff check .

Verificar que fitdecode está instalado e fitparse NÃO:
powershell

python -c "from importlib.metadata import version; print('fitdecode', version('fitdecode'))"
python -c "import fitparse" 2>&1   # esperado: ModuleNotFoundError

[Sessão 22 — primeira ação] Detecção de versão em produção (S21 — export CSV/GPX)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token

# Pega uma activity do prod para testar
$acts = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities?limit=5" -Headers @{ Authorization = "Bearer $token" }
$id = $acts[0].id

# CSV
$csv = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/export?format=csv" -Headers @{ Authorization = "Bearer $token" }
Write-Host "CSV: $($csv.StatusCode) $($csv.Headers['Content-Type'])"
Write-Host $csv.Content

# GPX (só se a activity tiver rota — has_bbox=True)
if ($acts[0].bbox) {
  $gpx = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/export?format=gpx" -Headers @{ Authorization = "Bearer $token" }
  Write-Host "GPX: $($gpx.StatusCode) $($gpx.Headers['Content-Type'])"
  Write-Host ($gpx.Content.Substring(0, [Math]::Min(300, $gpx.Content.Length)))
}

# Validação
try {
  Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/export?format=xpto" -Headers @{ Authorization = "Bearer $token" }
  Write-Host "ERRO: format invalido deveria dar 422"
} catch {
  Write-Host "OK: format invalido deu $($_.Exception.Response.StatusCode.value__)"
}

# Se compare=yoy responde 200 e format=xpto responde 422, o backend está na S21.

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

Validação do front em produção (browser) — primeira ação da S22

Manual em https://rumo-wheat.vercel.app:

    Login prod@rumo.com / senha12345.

    Abrir uma activity que tenha rota (mapa aparece).

    Conferir: "Baixar CSV" e "Baixar GPX" no cabeçalho, ao lado do título. "Baixar GPX" só aparece se houver rota.

    Clicar "Baixar CSV" → arquivo rumo_<id>_<type>.csv baixa; abrir no Excel/LibreOffice: 2 linhas, bbox_* preenchidos.

    Clicar "Baixar GPX" → arquivo rumo_<id>_<type>.gpx baixa; abrir em https://gpx.studio → trilha desenhada.

    Numa activity sem rota, "Baixar GPX" não aparece.

SEÇÃO 7 — DÍVIDAS TÉCNICAS

(FECHADA na S20) ~~Existem duas pastas de venv~~: .venv (fantasma) removida. Única venv é backend\venv (Python 3.13.7).

(FECHADA na S20) ~~Pylance reclamando de imports~~: .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"].

(CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type faz desempate em Python: items.sort(key=lambda r: (-r["total_activities"], r["activity_type"])). Qualquer novo ORDER BY em coluna Enum DEVE (a) fazer o sort final em Python, ou (b) ser testado contra a ordem de declaração.

(CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes de period DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias. Não misturar com _dt fixo.

(CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN. Quando um SELECT soma duas janelas, o WHERE deve cobrir a união. Cada métrica recorta via SUM(CASE WHEN <janela> THEN col ELSE 0 END).

(CONHECIDA — Sessão 17/18/19/20/21) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. O segmented control de período afeta APENAS a tabela por tipo. Intencional.

(CONHECIDA — Sessão 17/18/19/20) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. Isso NÃO é bug. Os 153 testes locais provam filtro e previous.

(CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática. Documentado em teste. Não é bug.

(CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — o <type> interno traduz para "walk" via map_gpx_type. Os testes de export usam activity.activity_type.value dinâmico em vez de hardcodar. Se trocar o sample, os testes continuam passando.

(CONHECIDA — Sessão 21) to_gpx não emite <time> por <trkpt> (a geometria guardada em route é só LineString, sem stream temporal — decisão da S10). O <trk> tem <name> e <type>, mas os pontos não têm timestamp individual. Strava/Garmin aceitam GPX assim. Se um dia a feature "export com timestamps" virar requisito, precisa ler raw_track_points (que tem [[lat, lon, ele, ts], ...]) em vez de route — mudança pontual em to_gpx + assinatura.

(CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. Não há caso de uso hoje (todo export exige auth). Adicionar quando aparecer (YAGNI).

(Oportunidade — S18/S19/S20/S21) Delta "vs. anterior / vs. ano anterior" cobre 3 métricas (atividades, distância, elevação). Tempo e calorias ficaram fora por legibilidade. Extensão trivial se virar requisito.

(Oportunidade — S18/S19/S20) Semântica do delta é NEUTRA (subiu=verde, desceu=vermelho, igual=cinza). Sem juízo de "melhor/pior". Se o produto quiser meta, é feature nova.

(Oportunidade — S19/S20) Stats públicas só aparecem quando viewer segue o alvo. "Stats públicas sempre" é mudança de regra em _ensure_can_view_stats (endpoint + teste + front). Não é bug — é decisão de privacidade documentada.

(Oportunidade) RouteMap.tsx é reutilizável. Se aparecer segundo uso, considerar React.lazy() para tirar o leaflet (163.60 kB) do chunk.

(Oportunidade — S21) Export em lote (ex.: GET /activities/export?format=gpx para todas as atividades do usuário, ou por período) — extensão natural do export unitário. Precisa decidir formato de ZIP vs. concatenado, e quais regras de auth (só as próprias? seguidas também?).

(Oportunidade — S21) Export no app mobile (mesma feature do web). Mobile está parado desde S11; seria sessão grande.

Mobile: sem drill-down de stats. Sem inclinação/rotação 3D. Sem export. TimeoutException do app mobile não reproduzido desde a Sessão 9.
SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 22 e além)
PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 22 (antes de qualquer mudança de código)

No terminal (PowerShell via Win+R → powershell):
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

Esperado: git push "Everything up-to-date"; HEAD == origin/main == 8936415 (ou o commit do handoff da S21, se já commitado); git status --short deve mostrar 3 linhas M (web/src/api/client.ts, web/src/api/activities.ts, web/src/pages/ActivityDetailPage.tsx) + M docs/HANDOFF.md se este handoff ainda não foi commitado.

Se as 3 linhas M estiverem lá: commitar o front (Seção 6). Se estiverem vazias: o front da S21 já foi commitado em outra sessão — conferir com git log e pular.

Depois, sanidade de build:
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
python -m pytest -q     # esperado: 153 passed
ruff check .

Depois, detecção de versão em produção (S21):
powershell

# bloco completo na Seção 6 ("Detecção de versão em produção (S21 — export CSV/GPX)")
# Esperado: CSV 200, GPX 200 (se rota), format=xpto 422

Depois, validação visual do front em produção (Seção 6 — bloco "Validação do front em produção (browser)"). Essa é a única parte da S21 não validada ainda. Se algo falhar, diagnosticar antes de qualquer outra coisa.
Estado da Rota B (fim da Sessão 21)

Quatro itens fechados na S20 (filtro de período, comparação com janela anterior, stats públicas em perfis de terceiros, comparação year-over-year). A S21 abriu e fechou a OPÇÃO 2 (export CSV/GPX). A Rota B "original" está concluída.
Próximos passos (escolha entre opções)

OPÇÃO 1 — Export em lote (CSV/GPX). ← RECOMENDADA

    Evolução natural do export unitário. Backend: GET /activities/export?format=csv|gpx&user_id=<opcional>&from=&to= (decidir se ZIP ou concatenado). Reaproveita to_gpx e _activity_to_csv.

    Front: botão "Exportar tudo" na ActivitiesPage ou ProfilePage.

    Escopo: 1 sessão de tamanho médio.

    Motivos: valor de produto direto (usuário já baixa 1; agora baixa N), contrato aditivo puro, testável 100% local.

OPÇÃO 2 — Export no app mobile (paridade com web).

    Mobile parado desde S11. Sessão grande. Só se houver demanda real.

    Não recomendo para S22 — sessão grande, alto risco, e o app mobile tem outras lacunas (sem stats drill-down, sem share).

OPÇÃO 3 — Resíduos de baixo risco (Rota A+).

    (b) RouteMap com React.lazy() — prepara para segundo uso. ~30 min.

    (c) Cheat sheet de endpoints num README.md. ~30 min.

    (d) ~~Remover .venv antiga~~ — feito na S20.

    Ganho marginal. Só se não houver Rota B clara.

OPÇÃO 4 — Export com timestamps por ponto.

    Muda to_gpx para ler raw_track_points (que tem [[lat, lon, ele, ts], ...]) em vez de route (que é só LineString). Mantém route para o mapa; export lê raw_track_points.

    Feature de nicho (Strava/Garmin aceitam GPX sem <time>, mas apps de análise preferem com). Custa pouco, mas não é prioridade.

OPÇÃO 5 — Export no mobile (paridade) ou "exportar tudo" via app.

    Combina com a Opção 1 + Opção 2. Só depois de decidir se o mobile vai evoluir.

Recomendação final para a Sessão 22

Antes de escolher, VALIDAR ESTADO (Seção 8 — primeira ação). Se tudo verde (build, lint, analyze, pytest 153, export respondendo em prod, botão funcionando no browser), aí escolher.

Rota recomendada: OPÇÃO 1 (export em lote).

Motivos:

    É a evolução natural do export unitário. O usuário baixa 1 atividade agora; a próxima pergunta é "e se eu quiser todas?".

    Reaproveita to_gpx e _activity_to_csv sem tocar em nada existente.

    Contrato aditivo puro: endpoint novo.

    Testável 100% local.

    Feature visível em ~1 sessão de tamanho médio.

Se o usuário preferir escopo menor: OPÇÃO 3 (React.lazy no RouteMap + README) — aquecimento de 30-60 min.

Se preferir escopo maior: OPÇÃO 2 (mobile) — mas avisar antes que é sessão grande.

Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 22 neste mesmo formato (seções 0 a 8).
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Pedido para o assistente da S22 (e além): manter o processo da S21. Concretamente:

    Fase 0 obrigatória: validar estado (git, build, lint, analyze, docker -a, pytest, detecção de versão em prod) antes de tocar em qualquer código.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. Pedir também models/activity.py, models/follow.py quando a feature tocar esses models.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — regra nova da S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (front) entre cada entrega. Nunca acumular 2 arquivos sem validar.

    Fase 4 — validação em produção: local verde é pré-requisito; prod via HTTP/browser é o que fecha.

    Fase 5 — handoff preventivo em ~70-80% do contexto, no formato completo (seções 0 a 8), sem resumir.

Regras novas da S21 (Seção 0, itens 7, 8, 9): nunca placeholder no código, não adivinhar nomes de símbolos, git status + git log antes de git restore.

O que funcionou nesta sessão (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros (o placeholder, o _client_as sem get_db, os 3 nomes errados) e correção com base no output real do terminal, não na previsão.