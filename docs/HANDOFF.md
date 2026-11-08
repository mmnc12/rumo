HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 20
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação sobre o projeto chega por DUAS vias:

(a) o usuário cola o conteúdo de um arquivo com Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal

NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere o usuário colar. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem (há script pronto na seção 6).

Sessões anteriores perderam tempo porque o assistente tentou "adivinhar" a árvore de diretórios e errou. Não repetir.
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos — o usuário precisa colar conteúdo e saídas de terminal.

PRODUÇÃO (na nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app). O backend de produção usa Postgres/PostGIS gerenciado. Testar via HTTP é sempre possível.

IMPORTANTE — usuário NÃO tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam automaticamente, validar via HTTP em produção. Não presumir que o usuário vai "rodar o app localmente" para testar UI.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (143 passed ao fim da Sessão 20). Container de teste rumo_postgres_test na porta 5433.

Para reativar numa sessão nova:

    Abrir Docker Desktop e esperar a baleia verde.

    Garantir que o terminal foi aberto via Win+R (fora do VS Code / Windows Terminal, que herdam PATH antigo).

    cd D:\Rumo\backend

    docker compose -f docker-compose.test.yml up -d

    .\venv\Scripts\Activate.ps1 (UM ponto, não dois)

    python -m pytest -q

VENV: ao fim da S20, a única venv é D:\Rumo\backend\venv (sem ponto), criada com Python 3.13.7. A .venv antiga (fantasma, quebrada) foi removida na S20 — dívida técnica da S19 fechada. .vscode/settings.json corrigido para apontar para backend/venv (não mais .venv) e ganhou python.analysis.extraPaths com backend.

ATENÇÃO: o py -3 deste Windows aponta para Python 3.14 (incompatível com as versões fixadas em requirements.txt — sem wheels cp314). Se precisar recriar a venv: py -3.13 -m venv D:\Rumo\backend\venv ou C:\Python313\python.exe -m venv D:\Rumo\backend\venv.
Estrutura do repo (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada na Sessão 19 e inalterada na S20 (só arquivos modificados, nenhum criado/removido):
text

D:\Rumo
├── .vscode
│   └── settings.json              # corrigido na S20 (backend/venv + extraPaths)
├── backend
│   ├── .pytest_cache
│   ├── .ruff_cache
│   ├── venv\                      # ATIVA (Python 3.13.7) — a única
│   ├── alembic
│   ├── app
│   │   ├── core
│   │   ├── models
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
│   │                              # test_follow.py + test_like.py + test_stats.py + __init__.py
│   ├── _scratch
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
├── docs
│   └── HANDOFF.md                 # este arquivo
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

Divergências vs handoff da Sessão 19: nenhuma estrutural. Só modificação de conteúdo em 7 arquivos (backend: stats_service.py, routers/activities.py, routers/users.py, tests/test_stats.py; web: api/stats.ts, hooks/useStats.ts, pages/ProfilePage.tsx) + remoção de .venv e correção de .vscode/settings.json.
Como rodar comandos Flutter no Windows deste usuário

Flutter instalado em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 (stable) / Dart 3.13.7 / DevTools 2.60.0.

PROBLEMA CONHECIDO: mesmo com C:\Users\nasci\flutter\bin no PATH, o PowerShell frequentemente NÃO reconhece o comando flutter (cache de sessão do terminal/VS Code). SOLUÇÃO QUE FUNCIONA: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Como rodar Docker e pytest local (Windows deste usuário)

Docker Desktop instalado em C:\Users\nasci\AppData\Local\Programs\DockerDesktop. docker.exe em ...\DockerDesktop\resources\bin\docker.exe. Esse caminho está no PATH do usuário. Se docker não for reconhecido, é porque o PowerShell foi aberto de dentro do VS Code / Windows Terminal (herda PATH antigo). SOLUÇÃO: abrir PowerShell via Win+R → "powershell".

Container de teste: rumo_postgres_test (5433). Containers permanentes rumo-redis (6379) e rumo-postgres (5432) NÃO são de teste.

Passos para pytest local:
text

PowerShell via Win+R → "powershell"
docker version (Client + Server) e docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps (rumo_postgres_test Up healthy na 5433)
.\venv\Scripts\Activate.ps1     # UM ponto, NÃO dois
python -m pytest -q             # esperado: 143 passed

Se Activate.ps1 der erro de política: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass.
Como testar o backend de produção sem o app (PowerShell)

Login (retorna JWT):
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me. /users/me devolve 422 (FastAPI tenta parsear "me" como UUID).
powershell

$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id

Contas de teste:

    prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341 (6 atividades, 26.443 m).

    Prod2 (id 01a141e7-5ea4-7600-8959-19145475ad0a) — 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2 (útil para cenário "terceiro seguido").

Para o cenário "terceiro NÃO seguido": usar a busca (/users/search?q=a) e escolher um id que não seja prod nem Prod2.

⚠️ Lições S18/S19/S20 — detecção de versão no ar:

    422 de versão NÃO distingue S17 de S18. O endpoint /activities/stats/by-type?period=30d devolve 422 desde a S17.

    Para S19: GET /users/{meId}/stats/summary responde 200 (não 404) e GET /users/me responde 422.

    Para S20: GET /activities/stats/by-type?period=90d&compare=yoy responde 200. E ?compare=xpto responde 422 (se der 200, o backend ainda está na S19).

⚠️ Lição S20 — previous: null em prod/Prod2 não é bug. Nenhuma das contas de teste tem atividade na janela de comparação (prod não tem >90d; Prod2 idem). previous: null é o esperado. Os 143 testes locais (com _dt_ago(400) para yoy) provam que a janela funciona.
O que o assistente precisa pedir ao usuário (não tem acesso a arquivos)

    Conteúdo de arquivos via Get-Content -Encoding UTF8 <caminho>. SEMPRE passar -Encoding UTF8; sem isso, acentos viram inÃ­cio.

    Saídas de comandos (flutter analyze, npm run build, git log, git status, pytest -q, ruff check).

    Nunca assumir estrutura "de cabeça": pedir o arquivo antes de reescrevê-lo.

ATENÇÃO — arquivos truncados/duplicados: se um Get-Content vier com a última linha cortada OU com o conteúdo DUPLICADO, NÃO adivinhar o final. Pedir ruff check <arquivo> (lista duplicatas de uma vez) e entregar o arquivo completo para Ctrl+A → colar → salvar.

ATENÇÃO — arquivo "salvo" que não salvou. SINTOMA: build ou pytest falha dizendo que um símbolo novo não existe, mesmo o assistente tendo entregado o arquivo. DIAGNÓSTICO: Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>". Se não aparecer, o disco ainda é o antigo. REGRA: depois de entregar um arquivo que muda contrato, pedir a confirmação com Get-Content | Select-String ANTES de rodar build/test.

ATENÇÃO — git diff pipeado no PowerShell pode exibir acentos como mojibake. É artefato de codepage do pipe, NÃO corrupção do arquivo.

ATENÇÃO — git log --oneline no PowerShell às vezes cola a última linha com o prompt seguinte. Não é corrupção; é formatação.

ATENÇÃO — git log sem --no-pager abre o less e trava o terminal. SEMPRE usar git --no-pager log ... ou prefixar com $env:PAGER="".

ATENÇÃO — Pylance reclamando de imports (fastapi/sqlalchemy/pytest) NÃO é erro de código. É interpretador errado. Na S20 a causa raiz foi identificada e corrigida: o .vscode/settings.json apontava para backend/.venv (removida) e não tinha python.analysis.extraPaths. Correção aplicada na S20: "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe" + "python.analysis.extraPaths": ["${workspaceFolder}/backend"]. Se voltar a acontecer: Ctrl+Shift+P → "Python: Select Interpreter" → D:\Rumo\backend\venv\Scripts\python.exe → Developer: Reload Window.

ATENÇÃO — save confirmado via Select-String (lição S20): o assistente previu "esperado vazio" e "esperado 0 ocorrências" em checks de validação, mas o output real tinha 4 e 9 ocorrências legítimas. Priorizar SEMPRE o output real do terminal em vez da expectativa do assistente. Quando o output divergir da previsão, investigar o output primeiro.
Acordos de trabalho (válidos em todas as sessões)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário. (Usuário reforçou isso nas S15–S20.)

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca "// resto igual". Preservar imports, comentários e trechos que já funcionam. Destacar o trecho alterado com comentário curto acima (// [Sessão N] ou // [Sessão N — fix]).

    UMA versão por arquivo por resposta. Se errar no meio do raciocínio, cortar a versão errada e entregar só a corrigida com nota de 1 linha. NUNCA duas versões do mesmo arquivo na mesma resposta.

    HANDOFF PREVENTIVO em ~70-80% do limite de contexto: parar o trabalho em curso e entregar o HANDOFF completo neste mesmo formato (seções 0 a 8), pronto para colar no próximo chat. Deve ser COMPLETO e bem explicado, não resumido.

    VALIDAÇÃO INCREMENTAL: quando a mudança toca mais de um arquivo da mesma stack, colar o(s) arquivo(s) base e rodar build/analyze antes de entregar o próximo — reduz superfície de erro. Exceção legítima: 2 arquivos acoplados por mudança de contrato interno (ex.: hook + consumidor do hook). Nesse caso, entregar os 2 juntos e rodar 1 build.

    VERIFICAR SAVE ANTES DE BUILD: quando o assistente entrega um arquivo com símbolo novo (tipo, função, param), pedir ao usuário Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>" antes de rodar build/test.

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 143 testes passando LOCALMENTE (pytest -q verde na Sessão 20), 0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon,minLat,maxLon,maxLat], n_points, simplified. 404 quando route é NULL.

ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax do PostGIS no mesmo SELECT (sem N+1). None quando route é NULL.

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.

        (S17) period opcional, default "all". Inválidos → 422.

        (S18) cada item tem previous (janela de comparação) ou null.

        (S20) compare opcional, default "prev". prev = janela imediatamente anterior. yoy = mesmo período do ano anterior. Inválido → 422.

Stats públicas em perfis de terceiros (S19 + S20):

    GET /users/{user_id}/stats/summary → StatsSummary

    GET /users/{user_id}/stats/weekly → StatsWeeklyResponse

    GET /users/{user_id}/stats/monthly → StatsMonthlyResponse

    GET /users/{user_id}/stats/by-type?period=X&compare=Y → StatsByTypeResponse

Regra de acesso (helper _ensure_can_view_stats em routers/users.py):

    self → 200, sem consulta extra.

    viewer segue target → 200.

    viewer não segue target → 403 ("Você precisa seguir este usuário pra ver as estatísticas dele").

    target não existe → 404 ("Usuário não encontrado") — 404, não 403, para não vazar existência.

Semântica de compare (S20):
period	compare	janela de comparação
all	qualquer	null (period all ignora compare)
90d	prev (default)	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide com prev — coincidência matemática documentada em teste)

Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet (RouteMap no detalhe) + recharts (gráficos no perfil). Drill-down por tipo tem segmented control de janela temporal (S17), coluna "vs. anterior" com delta colorido (S18), e desde a S20 um 2º segmented control "Comparar com:" (prev/yoy) que só aparece quando period !== "all". Header do delta alterna entre "vs. anterior" e "vs. ano anterior".

Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite), alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds. Intocado desde a S11. Sem drill-down de stats no app.
Entregas da Sessão 20

Backend — comparação year-over-year no drill-down por tipo.

    stats_service.py:

        Nova _yoy_window_expr(period) — simétrica à _previous_window_expr, deslocada 365 dias.

        Nova _comparison_window_expr(period, compare) — despacha para prev ou yoy.

        Nova _where_floor_days(period, compare) — limite inferior do WHERE: prev = 2N (inalterado), yoy = N + 365.

        get_by_type(..., compare: Literal["prev","yoy"] = "prev") — assinatura nova. prev byte-idêntico ao S18 (regressão zero). yoy usa _yoy_window_expr + _where_floor_days.

    routers/activities.py: +1 param compare em stats_by_type, repassado ao service.

    routers/users.py: +1 param compare em get_user_stats_by_type, repassado ao service.

    tests/test_stats.py: +7 testes na seção # ===== compare=prev|yoy ... [Sessão 20] =====:

        test_get_by_type_compare_yoy_90d_uses_year_ago_window — prova que yoy pega _dt_ago(400) (yoy) e ignora _dt_ago(120) (prev), enquanto prev pega o inverso.

        test_get_by_type_compare_yoy_90d_null_when_no_data_in_yoy_window — sem dado na yoy → previous: null mesmo com dado em prev.

        test_get_by_type_compare_yoy_1y_equals_prev — documenta coincidência 1y+prev ≡ 1y+yoy.

        test_get_by_type_compare_yoy_all_is_none — period=all ignora compare.

        test_route_by_type_compare_yoy_param — rota propaga compare=yoy.

        test_route_by_type_compare_invalid_returns_422 — compare=xpto → 422.

        test_route_by_type_compare_default_is_prev — sem compare, comportamento S18 preservado.

        Total: 143 passed.

Web — toggle year-over-year no drill-down.

    api/stats.ts:

        Novo export type StatsCompare = "prev" | "yoy".

        getStatsByType(period, compare?) e getUserStatsByType(userId, period, compare?) — compare opcional. Quando omitido, NÃO envia o param (if (compare) qs.set(...)), URL idêntica à S18/S19. Quando passado, envia ?compare=....

    hooks/useStats.ts:

        statsKeys.byType(period, compare?) → ["stats","by-type",period,compare ?? "prev"] (4 elementos).

        statsKeys.userByType(userId, period, compare?) → 6 elementos.

        useStatsByType(period, enabled, compare?) e useUserStatsByType(userId, canView, period?, compare?) — compare na key (default "prev" via ??), no queryFn (passa undefined se omitido → URL limpa).

    pages/ProfilePage.tsx:

        Novo estado byTypeCompare (default "prev").

        Novo COMPARE_FILTERS (pt-BR): "Período anterior" / "Mesmo período do ano anterior".

        Hook self: useStatsByType(byTypePeriod, isSelf, byTypeCompare).

        Hook user: useUserStatsByType(id, showOtherStats, byTypePeriod, byTypeCompare).

        Header do drill-down virou flex-col gap-2: linha 1 = título + period; linha 2 = compare (condicional a byTypePeriod !== "all").

        Header da coluna do delta: {byTypeCompare === "yoy" ? "vs. ano anterior" : "vs. anterior"}.

        Conteúdo interno (TYPE_FILTERS, TYPE_LABELS, PACE_TYPES, PERIOD_FILTERS, StatsCards, PeriodChart, PreviousDelta, DeltaLine, lista de atividades, abas, UserRow, computePace) intocado.

Higiene da S19 (fechada na S20):

    .venv fantasma removida (VS Code fechado + Stop-Process Code antes). Única venv agora é D:\Rumo\backend\venv.

    .vscode/settings.json corrigido: backend/.venv → backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"]. Pylance parou de reclamar.

Estado final: working tree limpo, HEAD == origin/main == 2ca4c81. pytest 143 passed / 0 warnings (local). ruff All checks passed. npm run build verde (824 modules, ProfilePage 18.32 kB). npm run lint limpo. flutter analyze sem issues (mobile não tocado). Render deployado (endpoints compare=prev|yoy respondendo em produção; compare=xpto → 422). Vercel redeployado e validado visualmente nos 4 cenários (self com period=90d, terceiro seguido, terceiro não seguido, Network sem compare=undefined).
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

Git (estado ao fim da Sessão 20):
text

2ca4c81 (HEAD -> main, origin/main) feat(web): toggle year-over-year no drill-down por tipo (Sessao 20)
879d885 feat(stats): comparacao year-over-year no drill-down por tipo (Sessao 20)
09a6596 docs: handoff da Sessao 19
0df0b9f feat(web): stats no perfil de terceiros seguidos (Sessao 19)
229e36b feat(users): stats publicas em perfis de terceiros (Sessao 19)
4ba08da docs: handoff da Sessao 18
b0e3a29 feat(stats): comparacao com janela anterior no drill-down por tipo (Sessao 18)
494d8cc docs: handoff da Sessao 17
5925a03 feat(stats): filtro de periodo no drill-down por tipo (90d|1y|all)
0f1c6ef chore(web): remove bboxToOsmTileUrl deprecated da Sessao 16

Todos os commits estão em origin/main (pushados). Render e Vercel deployam automático a cada push em main.
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 20
3.1 Validação de estado inicial

PowerShell via Win+R, repo em D:\Rumo. git push: Everything up-to-date. HEAD == origin/main == 09a6596 (handoff da S19). git status --short: limpo. npm run build: 824 modules, verde. flutter analyze: No issues found. Docker/compose OK. docker ps: rumo_postgres_test healthy na 5433. pytest -q: 136 passed. Endpoint /users/{meId}/stats/summary: 200 → S19 no ar.
3.2 Higiene da S19 (dívida técnica da venv)

    .venv fantasma identificada: só Scripts\ (sem pyvenv.cfg, sem Lib). venv (ativa) tinha home = C:\Python313, version = 3.13.7.

    ruff.exe em .venv\Scripts estava sendo segurado pelo VS Code (processo ruff — PID 23264). Stop-Process -Force não resolvia sozinho (VS Code reiniciava).

    Solução: Get-Process Code | Stop-Process -Force → Remove-Item -Recurse -Force .\.venv funcionou.

    .vscode/settings.json corrigido: backend/.venv → backend/venv + adicionado python.analysis.extraPaths: ["${workspaceFolder}/backend"]. Verificado com Select-String.

3.3 Decisão de rota: Opção 1 (year-over-year)

Rota escolhida após higiene. Motivos: evolução natural do drill-down; reaproveita 100% da infra das S17/S18; contrato aditivo (compare default "prev"); testável 100% local.

Contrato travado:

    compare=prev|yoy, default prev.

    previous mantém shape StatsByTypePreviousItem — sem campo comparison no response (decisão: o cliente sabe o que pediu, o label é decisão de UI).

    period="all" ignora compare → previous = null.

    period="1y" faz yoy ≡ prev (coincidência matemática, documentada em teste).

    UI: 2 segmented controls separados (period + compare); compare só aparece quando period !== "all".

3.4 Backend — implementação e testes

Ordem de entrega (1 arquivo por resposta): stats_service.py → routers/activities.py → tests/test_stats.py → routers/users.py. Cada um com ruff check + pytest.

Entrega 1 — stats_service.py: adicionado _yoy_window_expr, _comparison_window_expr, _where_floor_days; get_by_type ganhou compare param; WHERE ampliado para now - (N + 365) no modo yoy. Validado: ruff OK, pytest 136 (regressão zero), _where_floor_days sanity check: yoy 90d = 455, prev 90d = 180, yoy all = None.

Entrega 2 — routers/activities.py: +1 param compare em stats_by_type. Validado: ruff OK, pytest 136, rota registrada.

Entrega 3 — tests/test_stats.py: +7 testes S20 (detalhes na seção 1). Primeira entrega falhou em 2 testes (compare_yoy_90d_uses_year_ago_window e compare_default_is_prev) com previous is None em vez de 2000.0. Diagnóstico: os testes usavam _dt_ago(200), que cai fora da janela prev de 90d ([now-180, now-90)) e fora da yoy ([now-455, now-365)) — no "buraco" [now-365, now-180). Erro do teste, não do código. Corrigido: _dt_ago(200) → _dt_ago(120). 143 passed.

Entrega 4 — routers/users.py: +1 param compare em get_user_stats_by_type. Validado: ruff OK, pytest 143, rota registrada.

Commit 879d885 (feat(stats): comparacao year-over-year no drill-down por tipo (Sessao 20)) — push aceito.

Validação em produção:

    GET /activities/stats/by-type?period=90d&compare=yoy → 200, walk 3 atividades / 15.643,22 m / previous: null (esperado — prod não tem dado na janela yoy).

    GET /activities/stats/by-type?period=90d&compare=prev → 200, idêntico (regressão preservada).

    GET /users/{Prod2}/stats/by-type?period=90d&compare=yoy → 200, dados do alvo (2 atividades / 14.643,22 m / 0 kcal) — target_id respeitado.

    GET ...?compare=xpto → 422 — Literal do Pydantic.

3.5 Front — implementação

Ordem de entrega (1 arquivo por resposta, build entre cada):

    api/stats.ts: +StatsCompare, getStatsByType(period, compare?) e getUserStatsByType(userId, period, compare?). if (compare) qs.set(...) protege contra compare=undefined na URL. Validado: build verde (824 modules, ProfilePage 17.57 kB), tsc --noEmit limpo.

    hooks/useStats.ts: +statsKeys.byType(period, compare?) com compare ?? "prev" (determinístico, evita duplicação de cache entre undefined e "prev"), statsKeys.userByType(userId, period, compare?) idem. useStatsByType(period, enabled, compare?) e useUserStatsByType(userId, canView, period?, compare?). Validado: build verde (ProfilePage 17.61 kB).

    pages/ProfilePage.tsx: +StatsCompare import, +COMPARE_FILTERS, +estado byTypeCompare (default "prev"), hook self e user ganham byTypeCompare como último arg, header do drill-down virou flex-col gap-2 (linha 1 = título + period; linha 2 = compare, condicional), header da coluna delta alterna "vs. anterior" ↔ "vs. ano anterior". Validado: build verde (ProfilePage 18.32 kB), npm run lint limpo.

Commit 2ca4c81 (feat(web): toggle year-over-year no drill-down por tipo (Sessao 20)) — push aceito.
3.6 Validação visual (produção)

Conta prod@rumo.com. 4 cenários validados pelo usuário ("aparentemente tudo certo"):

    Self, period=90d: 2º control "Comparar com:" aparece com Período anterior ativo e Mesmo período do ano anterior. Ao trocar para yoy, header da coluna delta muda para "vs. ano anterior". Ao trocar period para "Todos", 2º control some e coluna delta some.

    Terceiro seguido (Prod2): mesmas ações, dados do Prod2 (2 atividades / 14.643 m / 0 kcal).

    Terceiro não seguido: sem seção de stats (regra S19 preservada).

    Network: URLs distintas para compare=prev e compare=yoy; quando period=all, URL fica ?period=all sem compare.

3.7 Estado final da sessão

    Working tree limpo, main == origin/main == HEAD == 2ca4c81.

    npm run build: verde (824 modules, ProfilePage 18.32 kB).

    npm run lint: limpo.

    pytest -q: 143 passed, 0 warnings (local).

    ruff check .: All checks passed.

    flutter analyze: No issues found (não tocado na S20).

    Backend em produção: endpoints compare=prev|yoy respondendo; compare=xpto → 422.

    Front em produção: validado visualmente nos 4 cenários.

    Nenhuma pendência de git.

3.8 Lições da Sessão 20 (importante)

O código entregue estava correto; as previsões de validação erraram 3 vezes:

    Disse "esperado 142 passed" — o correto era 143 (são 7 testes S20, não 6).

    Disse "esperado vazio" no Select-String de _dt_ago(200) — havia 4 ocorrências legítimas (dos testes S18/S20 pré-existentes).

    Disse "esperado 0 ocorrências" em previous.*total_distance_m.*3000.0 — regex mal-escrita (. sem escape, .* amplo). Output real tinha 9.

Regra para a S21: quando o output do terminal divergir da previsão do assistente, investigar o output real primeiro. Não assumir que o código quebrou — pode ser a previsão que está errada.

Os 2 testes que falharam na primeira entrega do test_stats.py eram erros de teste, não de código: _dt_ago(200) cai fora da janela prev de 90d e fora da yoy de 90d (no "buraco"). Corrigidos para _dt_ago(120).
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
GET /activities/stats/summary?activity_type=<opcional>

→ StatsSummary: total_activities, total_distance_m, total_duration_s, total_elevation_gain_m, total_calories, avg_pace_s_per_km, avg_speed_mps.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional>

→ StatsWeeklyResponse: { weeks, items: [StatsPeriod] }. StatsPeriod: period_start (segunda), total_activities, total_distance_m, total_duration_s, total_calories.
GET /activities/stats/monthly?months=N&activity_type=<opcional>

→ StatsMonthlyResponse: mesmo shape, chave months, period_start "YYYY-MM-01".
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy>

S17 + S18 + S20.

→ StatsByTypeResponse: { items: [StatsByTypeItem] }.

StatsByTypeItem: activity_type, total_activities, total_distance_m, total_duration_s, total_elevation_gain_m, total_calories, previous: StatsByTypePreviousItem | null.

StatsByTypePreviousItem: as 5 métricas (sem activity_type).

    Só tipos com >= 1 atividade na janela ATUAL aparecem.

    Ordenação: total_activities DESC, activity_type ASC (Python — enum nativo do Postgres ordena pela ordem de declaração, então desempate final é em Python).

    period inválido → 422. compare inválido → 422.

    previous null para period="all" ou tipo ausente na janela de comparação.

Janelas (S20):
period	compare	janela
all	qualquer	null
90d	prev	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide)
GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} (S19 + S20)

Mesmos shapes acima. by-type aceita period + compare (S20).

Permissão (helper _ensure_can_view_stats):

    self → 200.

    viewer segue target → 200.

    viewer não segue → 403 ("Você precisa seguir este usuário pra ver as estatísticas dele").

    target inexistente → 404 ("Usuário não encontrado").

Os 4 reaproveitam stats_service.* sem mudança de assinatura (by-type ganhou compare na S20).
GET /auth/me — identidade do usuário logado (NÃO é /users/me)

Resposta: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }.
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9 a 20 commitadas e pushadas. origin/main == main == HEAD == 2ca4c81.

Sessão 20 fechada com este handoff (a commitar como docs: handoff da Sessao 20 na próxima ação — geralmente primeira ação da S21).

Nenhuma pendência conhecida de git.
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 21 — primeira ação] Abrir PowerShell via Win+R → "powershell"

NÃO abrir de dentro do VS Code / Windows Terminal. Depois:
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

[Sessão 21 — primeira ação] Descoberta da estrutura do repo
powershell

Get-ChildItem -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app\routers -File | Select-Object Name
Get-ChildItem D:\Rumo\backend\tests -File | Select-Object Name

[Sessão 21 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 21 — primeira ação] Docker + pytest local
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps
# Se o prompt já mostra (venv), PULE a linha abaixo.
.\venv\Scripts\Activate.ps1      # UM ponto, NÃO dois
python -m pytest -q              # esperado: 143 passed

Verificar que fitdecode está instalado e fitparse NÃO:
powershell

python -c "from importlib.metadata import version; print('fitdecode', version('fitdecode'))"
python -c "import fitparse" 2>&1   # esperado: ModuleNotFoundError

[Sessão 21 — primeira ação] Detecção de versão em produção (S20 — year-over-year)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id
$resp = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=90d&compare=yoy" -Headers @{ Authorization = "Bearer $token" }
Write-Host "RESULTADO: S20 no ar (by-type?compare=yoy respondeu 200, items: $($resp.items.Count))"

Se der 404/422 → backend ainda está na S19. Se der 200 → S20 no ar. Para confirmar 422 no inválido:
powershell

try {
  Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=90d&compare=xpto" -Headers @{ Authorization = "Bearer $token" }
  Write-Host "ERRO: deveria ter dado 422"
} catch {
  Write-Host "OK: compare invalido deu $($_.Exception.Response.StatusCode.value__)"
}

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
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/monthly?months=6" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d&compare=prev" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d&compare=yoy" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

Quem prod segue (para o cenário "terceiro seguido")
powershell

$prod2Id = "01a141e7-5ea4-7600-8959-19145475ad0a"
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$prod2Id/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/01a12c83-be2a-71fa-b966-1c93ca64f341/following" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3

Stats do self (comparar com S18/S19)
powershell

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=all" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=90d&compare=prev" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=90d&compare=yoy" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

Ruff (backend)
powershell

cd D:\Rumo\backend
# Se o prompt já mostra (venv), pule:
.\venv\Scripts\Activate.ps1
ruff check .

SEÇÃO 7 — DÍVIDAS TÉCNICAS

(FECHADA na S20) ~~Existem duas pastas de venv~~: .venv (fantasma, só Scripts\) removida na S20 após Stop-Process Code. Única venv agora é backend\venv (Python 3.13.7).

(FECHADA na S20) ~~Pylance reclamando de imports~~: causa raiz era .vscode/settings.json apontando para .venv. Corrigido para backend/venv + python.analysis.extraPaths.

(CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO, não pela string. get_by_type faz o desempate final em Python: items.sort(key=lambda r: (-r["total_activities"], r["activity_type"])). REGRA: qualquer novo ORDER BY em coluna Enum DEVE (a) fazer o sort final em Python, ou (b) ser testado contra a ordem de declaração.

(CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes de period DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem >= 10 dias entre dentro e fora da janela. Não misturar com _dt fixo.

(CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN. Quando um SELECT precisa somar duas janelas, o WHERE deve cobrir a união (ex.: started_at >= now - 2N para prev, started_at >= now - (N+365) para yoy), e cada métrica recorta sua janela via SUM(CASE WHEN <janela> THEN col ELSE 0 END) — inclusive a contagem. Depois, filtrar em Python as linhas cuja janela principal ficou zerada.

(CONHECIDA — Sessão 17/18/19/20) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. O segmented control de período afeta APENAS a tabela por tipo. Intencional.

(CONHECIDA — Sessão 17/18/19/20) Conta prod@rumo.com não tem atividade >90d (na janela anterior nem na yoy). Por isso period=all, 90d e 1y retornam iguais em produção para prod, e previous vem null em todos os itens. Isso NÃO é bug. Para ver diferença em produção, usar Prod2 ou upload de GPX com data no passado. Não perder tempo achando que está quebrado — os 143 testes locais (com _dt_ago(120), _dt_ago(400), _dt_ago(500)) provam filtro e previous.

(CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática (a janela imediatamente anterior a 1 ano é o mesmo período do ano anterior). Documentado em teste (test_get_by_type_compare_yoy_1y_equals_prev). Não é bug.

(CONHECIDA — Sessão 20) compare só tem efeito visível em period="90d" (e em futuros períodos custom, tipo 30d/180d). Em period="1y", os dois valores dão o mesmo resultado. Em period="all", ambos dão null.

(Oportunidade — S18/S19/S20) Delta "vs. anterior / vs. ano anterior" cobre 3 métricas (atividades, distância, elevação). Tempo e calorias ficaram fora por legibilidade. Extensão trivial se virar requisito (mais 2 DeltaLine).

(Oportunidade — S18/S19/S20) Semântica do delta é NEUTRA (subiu=verde, desceu=vermelho, igual=cinza). Sem juízo de "melhor/pior". Se o produto quiser meta, é feature nova.

(Oportunidade — S19/S20) Stats públicas hoje só aparecem quando viewer segue o alvo. Se o produto quiser "stats públicas sempre" (ex.: perfil aberto), é mudança de regra no _ensure_can_view_stats (endpoint + teste + front). Não é bug — é decisão de privacidade documentada.

(Oportunidade) RouteMap.tsx é reutilizável. Se aparecer segundo uso, considerar React.lazy() para tirar o leaflet (163.60 kB) do chunk.

(Oportunidade) Drill-down por tipo poderia ganhar:

    Filtro de período custom (ex.: "últimos 180 dias"). Hoje é all|90d|1y fixo; adicionar valor ao Literal é aditivo.

    Export CSV/GPX (Opção 2 da Rota B — recomendada para S21).

    Year-over-year já implementado (S20). ✅

Mobile: sem drill-down de stats no app. Sem inclinação/rotação 3D. TimeoutException do app mobile não reproduzido desde a Sessão 9.
SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 21 e além)
PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 21 (antes de qualquer mudança de código)

No terminal (PowerShell via Win+R → "powershell"):
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short
cd web ; npm run build
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

Confirmar: push aceito, HEAD == origin/main == 2ca4c81 (ou o commit do handoff, se for o caso), build e analyze verdes, working tree limpo.

DOCKER + PYTEST LOCAL:
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps
# Se prompt já mostra (venv), pular:
.\venv\Scripts\Activate.ps1     # UM ponto
python -m pytest -q

Esperado: 143 passed, 0 warnings.

DETECÇÃO DE VERSÃO EM PRODUÇÃO (S20 — year-over-year):

Rodar o script da seção 6 ("Detecção de versão em produção (S20 — year-over-year)"). Esperado: by-type?compare=yoy responde 200 e compare=xpto responde 422. Se der 404/200 no inválido, o Render não redeployou — checar dashboard do Render.

DESCOBERTA DE ESTRUTURA (obrigatória — não adivinhar):

Rodar os Get-ChildItem da seção 6. Colar as saídas no chat ANTES de pedir ou reescrever qualquer arquivo.
Estado da Rota B (fim da Sessão 20)

Quatro itens fechados:

    Filtro de período (S17) — FEITO.

    Comparação com janela anterior (S18) — FEITO.

    Stats públicas em perfis de terceiros (S19) — FEITO.

    Comparação year-over-year (S20) — FEITO.

Higiene da S19 (venv + settings.json) — FEITA na S20.
Rota B — próximos passos (ESCOLHA entre opções)

OPÇÃO 2 — Export de atividades (CSV/GPX). ← RECOMENDADA

    Backend: endpoint novo GET /activities/{id}/export?format=csv|gpx (ou variante em lote). gpx_service.py já existe (parse de GPX no upload) — provavelmente reutilizável para geração (inverso).

    Front: botão "Baixar" no detalhe da atividade ou na lista. Precisa lidar com download de Blob (URL.createObjectURL).

    Escopo maior que year-over-year, mas coeso. Feature visível nova. Testável 100% local.

    Motivos para recomendar: valor de produto direto, reaproveita infra existente, contrato aditivo, sem dependência de terceiros.

OPÇÃO 3 — Stats no app mobile (drill-down por tipo no Flutter).

    Mobile está parado desde S11. Se for evoluir, é sessão grande.

    Decidir se vale antes de começar. Paridade com web está longe.

    Não recomendo para a S21 — sessão grande, alto risco, pouco valor incremental no estado atual do app.

OPÇÃO 4 — Resíduos de baixo risco da Rota A+.

    (b) RouteMap com React.lazy() — prepara terreno para segundo uso.

    (c) Cheat sheet de endpoints num README.

    (d) ~~Remover .venv antiga~~ — FEITO na S20.

    Ganho marginal. Só se não houver Rota B clara.

Recomendação final para a Sessão 21

Antes de escolher, VALIDAR ESTADO (seção 6 — primeira ação). Se estiver tudo verde (build, analyze, pytest 143, compare=yoy no ar, compare=xpto → 422), aí escolher.

Rota recomendada: OPÇÃO 2 (export CSV/GPX).

Motivos:

    É a evolução natural do produto depois das stats. O usuário já vê seus dados agregados; agora quer levar os dados brutos.

    gpx_service.py já existe (parse no upload) — inverso (geração) reaproveita a mesma lib (gpxpy).

    Contrato aditivo puro: endpoint novo, nada existente muda.

    Testável 100% local.

    Feature visível em ~1 sessão de tamanho médio.

Se o usuário preferir escopo menor: OPÇÃO 4 (React.lazy no RouteMap + README) — aquecimento de 30-60 min.

Se o usuário preferir escopo maior: OPÇÃO 3 (mobile) — mas avisar antes que é sessão grande.

Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 21 neste mesmo formato (seções 0 a 8).