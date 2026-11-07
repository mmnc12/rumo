HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 16

===============================================================================

    LEIA PRIMEIRO — CONTEXTO OPERACIONAL (evita retrabalho no próximo chat)
    ===============================================================================

⚠️ REGRA DE OURO PARA O ASSISTENTE NOVO (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir
arquivo", "ver o repo". Toda informação sobre o projeto chega por DUAS vias:
(a) o usuário cola o conteúdo de um arquivo com Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal
NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA
reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um
arquivo, PEÇA e espere o usuário colar. Se a estrutura de pastas for
necessária, PEÇA a saída de Get-ChildItem (há script pronto na seção 6).
Sessões anteriores perderam tempo porque o assistente tentou "adivinhar" a
árvore de diretórios e errou. Não repetir.

O QUE É LOCAL vs O QUE É PRODUÇÃO

    LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI

        Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 +
        TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter).
        O assistente NÃO tem acesso a esses arquivos neste chat — o usuário precisa
        colar conteúdo de arquivos e saídas de terminal.

    PRODUÇÃO (na nuvem, acessível por HTTP): backend no Render
    (https://rumo-api-5s0b.onrender.com), frontend web na Vercel
    (https://rumo-wheat.vercel.app). O backend de produção usa Postgres/PostGIS
    gerenciado. Testar via HTTP é sempre possível.

    DOCKER: INSTALADO E FUNCIONAL no Windows local. pytest -q local verde
    (118 passed ao fim da Sessão 16). Container de teste rumo_postgres_test
    na porta 5433. Para reativar numa sessão nova: (1) abrir Docker Desktop e
    esperar a baleia verde; (2) garantir que o terminal foi aberto via Win+R
    (fora do VS Code / Windows Terminal, que herdam PATH antigo); (3) docker compose -f docker-compose.test.yml up -d; (4) pytest -q.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada no início da Sessão 16:

D:\Rumo
├── .vscode
├── backend
│ ├── .pytest_cache
│ ├── .ruff_cache
│ ├── .venv\ # virtualenv Python ativo (..venv\Scripts\Activate.ps1)
│ ├── alembic
│ ├── app
│ │ ├── core
│ │ ├── models
│ │ ├── routers\ # activities.py, auth.py, comments.py, feed.py,
│ │ │ # notifications.py, photos.py, users.py, init.py
│ │ ├── schemas
│ │ ├── services\ # activity_service.py, comment_service.py, errors.py,
│ │ │ # feed_service.py, fit_service.py, follow_service.py,
│ │ │ # gpx_service.py, like_service.py, notification_service.py,
│ │ │ # photo_service.py, stats_service.py, user_service.py
│ │ └── pycache
│ ├── samples
│ ├── scripts
│ ├── tests\ # conftest.py + test_calories.py + test_comment.py +
│ │ # test_follow.py + test_like.py + test_stats.py
│ ├── _scratch
│ ├── docker-compose.test.yml
│ ├── pytest.ini
│ └── requirements.txt
├── docs
│ └── HANDOFF.md # este arquivo
├── mobile
│ └── lib
│ ├── models\ # activity.dart, activity_track.dart, comment.dart
│ ├── pages\ # activity_detail_page.dart, feed_page.dart,
│ │ # login_page.dart
│ ├── services
│ └── widgets\ # activity_map.dart, like_button.dart (flat)
└── web
└── src
├── api\ # activities.ts, auth.ts, client.ts, notifications.ts,
│ # photos.ts, social.ts, stats.ts (getStatsByType)
├── assets
├── components\ # ActivityCard, ActivityResults, AppHeader,
│ # CommentsSection, LikeButton, NotificationBell,
│ # PeriodChart (unifica 4 gráficos), PhotoGallery,
│ # PhotoUpload, ProtectedRoute, RouteMap, StatsCards,
│ # UserResults
├── contexts
├── hooks\ # useActivities, useActivitySearch, useAuth, useDebounce,
│ # useNotifications, usePhotos, useProfile, useSocial,
│ # useStats (useStatsByType), useUserSearch
├── lib\ # format.ts (format* + formatElevation — S15),
│ # geo.ts (bboxToOsmTileUrl — S11;
│ # bboxToOsmTileGrid — S16)
├── pages\ # ActivitiesPage, ActivityDetailPage, FeedPage,
│ # LoginPage, NotificationsPage, ProfilePage,
│ # RegisterPage, SearchPage, UploadPage
└── types\ # api.ts (todos os tipos, StatsByType* — S14)

DIVERGÊNCIAS vs handoff da Sessão 15:

    web/src/lib/geo.ts ganhou bboxToOsmTileGrid (mosaico 2×2) — S16.
    bboxToOsmTileUrl continua existindo, marcada @deprecated, sem uso atual.

    web/src/components/ActivityCard.tsx passou a usar o mosaico 2×2 — S16.

    Mobile NÃO mudou na S16 (activity_map.dart já cobria a bbox via
    CameraFit.bounds desde a S11; sem tocar).

Se um arquivo específico for necessário, o pedido correto é:
Get-Content -Encoding UTF8 <caminho completo>
E o script de descoberta (primeira ação de sessão) está na seção 6.

COMO RODAR COMANDOS FLUTTER NO WINDOWS DESTE USUÁRIO

    Flutter instalado em: C:\Users\nasci\flutter (bin em ...\flutter\bin).

    Versões: Flutter 3.47.9 (stable) / Dart 3.13.7 / DevTools 2.60.0.

    PROBLEMA CONHECIDO: mesmo com C:\Users\nasci\flutter\bin no PATH do usuário
    e flutter.bat existindo, o PowerShell frequentemente NÃO reconhece o
    comando flutter — é cache de sessão do terminal/VS Code.

    SOLUÇÃO QUE FUNCIONA (usar por padrão):
    & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>

    Repo/repo mobile: D:\Rumo e D:\Rumo\mobile. PowerShell, Windows 5.1.

COMO RODAR DOCKER E PYTEST LOCAL (Windows deste usuário)

    Docker Desktop instalado em:
    C:\Users\nasci\AppData\Local\Programs\DockerDesktop

    O executável docker.exe está em:
    C:\Users\nasci\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe

    Este caminho ESTÁ no PATH do usuário. Se docker não for reconhecido,
    é porque o PowerShell foi aberto de dentro do VS Code / Windows Terminal
    (herda PATH antigo). SOLUÇÃO: abrir PowerShell via Win+R → "powershell".

    Container de teste: rumo_postgres_test (5433). Containers permanentes
    rumo-redis (6379) e rumo-postgres (5432) NÃO são de teste.

    Passos para pytest local:

        PowerShell via Win+R → "powershell"

        docker version (Client + Server) e docker compose version

        cd D:\Rumo\backend

        docker compose -f docker-compose.test.yml up -d

        docker ps (rumo_postgres_test Up healthy na 5433)

        .\.venv\Scripts\Activate.ps1 (prompt vira (.venv))

        pytest -q — esperado: 118 passed, 0 warnings (verde na Sessão 16)

    Se Activate.ps1 der erro de política:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

COMO TESTAR O BACKEND DE PRODUÇÃO SEM O APP (PowerShell)

    Login (retorna JWT):
    body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodytoken = $login.access_token

    Feed (com bbox):
    token" }

    Track de uma atividade:
    t=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities/t=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities/id/track" -Headers @{ Authorization = "Bearer $token" }

    Stats (todos validados em produção):
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3 Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/monthly?months=6" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3 Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3

    Conta de teste: prod@rumo.com / senha12345.

O QUE O ASSISTENTE PRECISA PEDIR AO USUÁRIO (não tem acesso a arquivos)

    Conteúdo de arquivos via: Get-Content -Encoding UTF8 <caminho>
    (SEMPRE passar -Encoding UTF8; sem isso, acentos viram "inÃ­cio".)

    Saídas de comandos (flutter analyze, npm run build, git log, git status,
    pytest -q, ruff check).

    Nunca assumir estrutura "de cabeça": pedir o arquivo antes de reescrevê-lo.

    ATENÇÃO — arquivos truncados/duplicados: se um Get-Content vier com a
    última linha cortada OU com o conteúdo DUPLICADO, NÃO adivinhar o final.
    Pedir ruff check <arquivo> (lista duplicatas de uma vez) e entregar o
    arquivo completo para Ctrl+A → colar → salvar.

    ATENÇÃO — git diff pipeado no PowerShell pode exibir acentos como
    mojibake. É artefato de codepage do pipe, NÃO corrupção do arquivo.

    ATENÇÃO — git log --oneline no PowerShell às vezes cola a última linha
    com o prompt seguinte. Não é corrupção; é formatação.

    ATENÇÃO — git log sem --no-pager abre o less e trava o terminal.
    SEMPRE usar git --no-pager log ... ou prefixar com $env:PAGER="".

ACORDOS DE TRABALHO (válidos em todas as sessões)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão
    pendente, executar a recomendada salvo instrução explícita em contrário.
    (Usuário reforçou isso no início da Sessão 15 e de novo na Sessão 16.)

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff
    parcial, nunca "// resto igual". Preservar imports, comentários e trechos
    que já funcionam. Destacar o trecho alterado com comentário curto acima
    (// [Sessão N] ou // [Sessão N — fix]).

    UMA versão por arquivo por resposta. Se errar no meio do raciocínio,
    cortar a versão errada e entregar só a corrigida com nota de 1 linha.
    NUNCA duas versões do mesmo arquivo na mesma resposta.

    HANDOFF PREVENTIVO em ~70-80% do limite de contexto: parar o trabalho em
    curso e entregar o HANDOFF completo neste mesmo formato (seções 0 a 8),
    pronto para colar no próximo chat. Handoff deve ser COMPLETO e bem
    explicado, não resumido.

    VALIDAÇÃO INCREMENTAL: quando a mudança toca mais de um arquivo da mesma
    stack, colar o(s) arquivo(s) base e rodar build/analyze antes de entregar
    o próximo — reduz superfície de erro. (S16 fez isso com geo.ts → build →
    ActivityCard.tsx → build.)

===============================================================================

    TL;DR PARA QUEM CHEGA AGORA
    ===============================================================================

    Backend: 118 testes passando LOCALMENTE (pytest -q verde na Sessão 16),
    0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track
    devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat],
    bbox [minLon,minLat,maxLon,maxLat], n_points, simplified. 404 quando
    route é NULL.

    ActivityResponse (feed/lista/detalhe/busca) inclui
    bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax do PostGIS
    no mesmo SELECT (sem N+1). None quando route é NULL.

    Endpoints de stats (todos validados em produção):

        GET /activities/stats/summary — StatsSummary.

        GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

        GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

        GET /activities/stats/by-type — StatsByTypeResponse.
        Os 3 primeiros aceitam activity_type opcional. O by-type NÃO aceita.

    Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet
    (RouteMap no detalhe) + recharts (gráficos no perfil).

    Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
    alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds.

    [Sessão 16 — entregas]

        Miniatura do feed (web) — mosaico 2×2 de tiles OSM.

            web/src/lib/geo.ts: +bboxToOsmTileGrid(bbox, zoom=13) retornando
            OsmTileGrid { tiles: OsmTile[4], zoom, center }. OsmTile tem
            { url, row: 0|1, col: 0|1 }. Ordem NW/NE/SW/SE.
            bboxToOsmTileUrl preservada, marcada @deprecated.

            web/src/components/ActivityCard.tsx: import trocado para
            bboxToOsmTileGrid; bloco de miniatura virou <div grid grid-cols-2 grid-rows-2 h-24> com 4 <img>. Comentário // [Sessão 16 — fix].

            Sem importar react-leaflet no card — leaflet continua isolado em
            chunk próprio (163.60 kB gzip 48.18 kB), fora do feed.

            npm run build: 824 modules, 1.57s, verde. index-*.js cresceu
            +190 bytes; CSS +50 bytes.

            Commit: a8a515f.

        Miniatura do feed (mobile) — INVESTIGAÇÃO, sem mudança.

            mobile/lib/widgets/activity_map.dart já cobria a bbox inteira via
            flutter_map + CameraFit.bounds desde a Sessão 11. Não corta
            bordas. Reescrever para mosaico seria regressão (abandonaria o
            auto-fit).

            mobile/lib/pages/feed_page.dart já tem guarda if (activity.bbox != null) antes de chamar ActivityMap.fromBbox. Sem placeholder
            cinza no feed de atividades sem rota.

            Decisão: NÃO alterar o mobile. Dívida registrada na seção 7.

        Estado final: working tree limpo, HEAD == origin/main == a8a515f,
        pytest 118 passed / 0 warnings, npm run build verde (824 modules),
        flutter analyze sem issues.

===============================================================================

    PRODUÇÃO E AMBIENTE
    ===============================================================================

    Backend: https://rumo-api-5s0b.onrender.com

    Docs Backend: https://rumo-api-5s0b.onrender.com/docs

    Frontend Web: https://rumo-wheat.vercel.app

    Repo local: D:\Rumo

    Mobile: D:\Rumo\mobile

    Web: D:\Rumo\web (scripts: "build": "tsc -b && vite build", "lint": "eslint .")

    Flutter: 3.47.9 / Dart 3.13.7

    Docker Desktop: 4.93.0 (engine 29.8.1, compose v5.5.1)

    SO: Windows, PowerShell 5.1

    Venv backend: D:\Rumo\backend.venv (ativa com ..venv\Scripts\Activate.ps1)

    Git (estado ao fim da Sessão 16):
    a8a515f (HEAD -> main, origin/main) feat(web): miniatura do feed em mosaico 2x2 de tiles OSM
    05185f0 docs: handoff da Sessão 15
    4cfd099 refactor(web): StatsCards usa formatElevation em vez de inline
    fdac345 feat(web): coluna de elevacao no drill-down por tipo
    3cf7668 refactor(backend): migra parsing de .FIT de fitparse para fitdecode
    d7d756e docs: registra entregas da Sessao 15 (A-a, A-b) e decisao sobre enums
    053239c feat(web): coluna de pace medio no drill-down por tipo
    fa4fcc4 test(backend): silencia deprecation do fitparse via filterwarnings no pytest.ini

    Todos os commits estão em origin/main (pushados).

    Render e Vercel deployam automático a cada push em main. O mosaico 2×2
    já está no ar (deploy da Vercel disparou no push de a8a515f).

===============================================================================

    O QUE FOI FEITO NA SESSÃO 16
    ===============================================================================

3.1 Validação de estado inicial (Sessão 16)

    PowerShell via Win+R, repo em D:\Rumo, venv backend ativo.

    git push: Everything up-to-date.

    HEAD == origin/main == 05185f0 (commit do handoff da S15).

    git status --short: limpo.

    npm run build: 824 modules, 1.77s, verde.

    flutter analyze: No issues found (51.1s).

    docker version: Client/Server 29.8.1. compose v5.5.1.

    rumo_postgres_test: Up healthy na 5433.

    pytest -q: 118 passed em 29.77s, 0 warnings.

    python -c "import fitdecode": 0.11.0 OK.

    python -c "import fitparse": ModuleNotFoundError (esperado).

    Descoberta de estrutura via Get-ChildItem: bate com o handoff da
    Sessão 15, sem divergências.

3.2 [Web] Rota A+ (a) — miniatura do feed em mosaico 2×2

    Lidos web/src/components/ActivityCard.tsx e
    web/src/components/RouteMap.tsx.

    Análise: RouteMap é leaflet interativo (MapContainer, Polyline,
    useMap, fit bounds). Puxar para o card significaria leaflet no feed
    inteiro (163.60 kB gzip 48 kB) — descartado.

    Análise: bboxToOsmTileUrl (S11) usa 1 tile de zoom 12 centralizado
    no bbox. Rotas com bbox maior que 1 tile cortam bordas.

    Lido web/src/lib/geo.ts (função única, TS puro).

    Entrega 1/2 (validada isoladamente):

        lib/geo.ts ganhou OsmTile, OsmTileGrid,
        bboxToOsmTileGrid(bbox, zoom=13). bboxToOsmTileUrl preservada
        e marcada @deprecated.

        npm run build: 824 modules, 2.00s, verde. Nada importado ainda —
        aditivo.

    Entrega 2/2:

        ActivityCard.tsx importa bboxToOsmTileGrid; variável
        mapTileUrl: string | null virou mapGrid: OsmTileGrid | null;
        render virou <div grid grid-cols-2 grid-rows-2 h-24> com 4
        <img> mapeados por ${tile.row}-${tile.col}.

        Resto intacto: author, cover_photo_url, emoji, título, métricas,
        botão de like, HeartIcon, comentários originais onde faziam
        sentido. // [Sessão 16 — fix] no bloco alterado.

        npm run build: 824 modules, 1.57s, verde. index-.js +190 bytes;
        index-.css +50 bytes. leaflet-*.js inalterado em 163.60 kB.

    Commit: a8a515f.

3.3 [Mobile] Rota A+ (a) — investigação, sem mudança

    Listados mobile/lib/widgets (2 arquivos: activity_map.dart,
    like_button.dart) e mobile/lib/pages (3 arquivos:
    activity_detail_page.dart, feed_page.dart, login_page.dart).

    Lido activity_map.dart:

        Modo bbox (miniatura) já usa flutter_map com
        CameraFit.bounds(bounds, padding: EdgeInsets.all(8)) —
        auto-fit da bbox inteira. Cobre a bbox em qualquer tamanho
        (TileLayer carrega quantos tiles precisar).

        Modo track (detalhe): polyline + pinos + toggle Mapa/Satélite.

        Não corta bordas — o problema que a dívida descreve não se aplica
        ao mobile.

    Lido feed_page.dart:

        Bloco da miniatura está dentro de if (activity.bbox != null) ...[ ... ActivityMap.fromBbox(bbox: activity.bbox!, height: 120) ].

        Ou seja: sem rota = sem miniatura, sem _MapPlaceholder cinza.
        Mesmo comportamento do web.

    Decisão: NÃO alterar o mobile. Unificar com o web significaria
    abandonar CameraFit.bounds (que já funciona) para replicar um
    cálculo manual — regressão, não melhoria.

    Dívida registrada (seção 7): abordagens divergentes web vs. mobile.

3.4 Estado final da sessão

    Working tree limpo, main == origin/main == a8a515f.

    npm run build: verde (824 modules).

    pytest -q: 118 passed, 0 warnings (local).

    flutter analyze: No issues found.

    Nenhuma pendência de git.

===============================================================================

    CONTRATOS DO BACKEND RELEVANTES (referência)
    ===============================================================================

    GET /activities/{id}/track (auth: Bearer JWT)
    Permissão: dono OU seguidor do dono (404 caso contrário).
    404 quando activity.route is None → detail "Atividade não possui rota".
    Resposta (TrackResponse):
    {
    "activity_id": "uuid",
    "type": "LineString",
    "coordinates": [[lon, lat], [lon, lat], ...], // GeoJSON
    "bbox": [minLon, minLat, maxLon, maxLat],
    "n_points": 60,
    "simplified": false
    }

    ActivityResponse (feed/lista/detalhe/busca):
    {
    ...,
    "bbox": [minLon, minLat, maxLon, maxLat] // ou null
    }
    Ordem GeoJSON. Null quando route IS NULL. Sem N+1.

    ActivityResponse NÃO inclui route nem coordinates (polyline só via /track).

    GET /activities/stats/summary?activity_type=<opcional>
    → StatsSummary:
    {
    "total_activities": 6,
    "total_distance_m": 26443.22,
    "total_duration_s": 18679,
    "total_elevation_gain_m": 5411.6,
    "total_calories": 1091,
    "avg_pace_s_per_km": 706.38,
    "avg_speed_mps": 1.42
    }

    GET /activities/stats/weekly?weeks=N&activity_type=<opcional>
    → StatsWeeklyResponse:
    {
    "weeks": 8,
    "items": [
    {
    "period_start": "2026-11-02", // sempre segunda-feira
    "total_activities": 1,
    "total_distance_m": 1000.0,
    "total_duration_s": 600,
    "total_calories": 41
    },
    ...
    ]
    }

    GET /activities/stats/monthly?months=N&activity_type=<opcional>
    → StatsMonthlyResponse: mesmo shape do weekly, period_start é sempre
    "YYYY-MM-01", chave "months".

    GET /activities/stats/by-type (S14 — sem query params)
    → StatsByTypeResponse:
    {
    "items": [
    {
    "activity_type": "run", // string
    "total_activities": 12,
    "total_distance_m": 84000.0,
    "total_duration_s": 25200,
    "total_elevation_gain_m": 1200.0,
    "total_calories": 4200
    },
    ...
    ]
    }
    Só tipos com >= 1 atividade. Ordenação garantida: total_activities DESC,
    activity_type ASC (aplicado em Python, não no SQL).

    Todos os endpoints de stats são do current_user (não aceitam user_id).
    A UI só mostra stats no próprio perfil (isSelf).

===============================================================================

    COMMITS PENDENTES / ESTADO DO REPO
    ===============================================================================

    Sessões 9 a 16 commitadas e pushadas.

    origin/main == main == HEAD == a8a515f.

    Sessão 16 fechada com este handoff (commit docs: handoff da Sessão 16).

    Nenhuma pendência conhecida de git.

===============================================================================

    SCRIPTS ÚTEIS (PowerShell)
    ===============================================================================

[Sessão 17 — primeira ação] Abrir PowerShell via Win+R → "powershell"
(NÃO abrir de dentro do VS Code / Windows Terminal)
Depois:
[Sessão 17 — primeira ação] Estado do repo (sem abrir o less)

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short
[Sessão 17 — primeira ação] Descoberta da estrutura do repo

Get-ChildItem -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app\routers -File | Select-Object Name
Get-ChildItem D:\Rumo\backend\tests -File | Select-Object Name
[Sessão 17 — primeira ação] Sanidade de build

cd D:\Rumo\web
npm run build

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
[Sessão 17 — primeira ação] Docker + pytest local

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps
..venv\Scripts\Activate.ps1
pytest -q
Verificar que fitdecode está instalado e fitparse NÃO

python -c "import fitdecode; print('fitdecode OK:', fitdecode.version)"
python -c "import fitparse" 2>&1 # esperado: ModuleNotFoundError
Login (produção)

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodytoken = $login.access_token
Feed com bbox (produção)

token" }
(.id.Substring(0,8))title=.​id.Substring(0,8))title=(.title)bbox=.​title)bbox=($_.bbox -join ',')" }
Stats (produção)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3 Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/monthly?months=6" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3 Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3
Track (produção)

t=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities/t=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities/id/track" -Headers @{ Authorization = "Bearer $token" }
Ruff (backend)

cd D:\Rumo\backend
..venv\Scripts\Activate.ps1
ruff check .

===============================================================================

    DÍVIDAS TÉCNICAS
    ===============================================================================

    (ARMADILHA CONHECIDA — decisão da Sessão 14, documentada na S15)
    Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO, não pela
    string. Activity.activity_type é Enum nativo (run, walk, cycle, hike,
    swim, other). ORDER BY activity_type no SQL devolve nessa ordem.
    DECISÃO: get_by_type (stats_service.py) faz o desempate final em Python:
    items.sort(key=lambda r: (-r["total_activities"], r["activity_type"]))
    REGRA PARA O FUTURO: qualquer novo ORDER BY em coluna Enum DEVE (a) fazer
    o sort final em Python, ou (b) ser explicitamente testado contra a ordem
    de declaração do enum. Não confiar em ORDER BY direto em coluna Enum.

    (NOVA — Sessão 16) Miniatura do feed — abordagens divergentes entre web e
    mobile.

        Web: mosaico 2×2 manual de tiles OSM (bboxToOsmTileGrid, zoom 13,
        enquadramento pelo centro do bbox).

        Mobile: flutter_map + CameraFit.bounds auto-fit da bbox inteira
        (ActivityMap.fromBbox, desde a S11).
        Ambos resolvem "não cortar bordas"; a diferença é visual (nível de
        detalhe e área coberta). NÃO UNIFICAR sem necessidade real — as duas
        soluções são nativas de cada stack, e qualquer unificação sairia pior
        que o estado atual. Reavaliar só se o usuário reclamar de divergência
        visual entre superfícies.

    (Oportunidade) bboxToOsmTileUrl (web) ficou @deprecated e sem uso
    após a S16. Se ninguém reativar, remover numa sessão futura (commit
    pequeno, sem impacto).

    (Oportunidade) RouteMap.tsx é reutilizável em qualquer página que
    renderize uma rota. Hoje só é usado em ActivityDetailPage. Se aparecer
    um segundo uso, considerar React.lazy() para tirar o leaflet (163.60 kB)
    do chunk da página que não mostra mapa. Ganho hoje é marginal.

    Web: miniatura agora é mosaico 2×2, mas ainda não desenha a polyline por
    cima. Para desenhar rota na miniatura seria preciso serviço externo
    (staticmap com polyline) ou leaflet estático — nenhum dos dois vale o
    custo hoje.

    Mobile: sem inclinação/rotação 3D (flutter_map é 2D). Se 3D for
    requisito, avaliar maplibre_gl (decisão maior, pesada).

    TimeoutException do app mobile não reproduzido desde a Sessão 9.
    Registrar se voltar (tela + log do flutter run).

    (Oportunidade) Drill-down de stats por tipo poderia ganhar:

        Filtro por período (ex.: "últimos 90 dias"). Hoje mostra "todos os
        tempos".

        Comparação "este período vs. anterior".

    (Oportunidade) Stats no perfil: /activities/stats/summary, /weekly,
    /monthly e /by-type são só do current_user. Se um dia o requisito for
    "ver stats de outro usuário", precisa de novos endpoints (com
    privacidade, provavelmente via follow).

===============================================================================

    PRÓXIMOS PASSOS RECOMENDADOS (Sessão 17 e além)
    ===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 17 (antes de qualquer mudança de código):

    No terminal (PowerShell via Win+R → "powershell"):
    cd D:\Rumo
    git push
    git --no-pager log --oneline -8
    git status --short
    cd web ; npm run build
    cd ..\mobile
    & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
    Confirmar: push aceito, HEAD == origin/main == a8a515f (ou o commit do
    handoff), build e analyze verdes, working tree limpo.

    DOCKER + PYTEST LOCAL:
    docker version
    docker compose version
    cd D:\Rumo\backend
    docker compose -f docker-compose.test.yml up -d
    docker ps
    ..venv\Scripts\Activate.ps1
    pytest -q
    Esperado: 118 passed, 0 warnings.

    DESCOBERTA DE ESTRUTURA (obrigatória — não adivinhar):
    cd D:\Rumo
    Get-ChildItem -Directory | Select-Object Name
    Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
    Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
    Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
    Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
    Get-ChildItem D:\Rumo\backend\app -Directory | Select-Object Name
    Get-ChildItem D:\Rumo\backend\app\routers -File | Select-Object Name
    Get-ChildItem D:\Rumo\backend\tests -File | Select-Object Name
    Colar as saídas no chat ANTES de pedir ou reescrever qualquer arquivo.

ESTADO DA ROTA A+ (Sessão 16): FECHADA.
(a) miniatura do feed → FEITO no web (a8a515f); mobile já estava OK.
(b) coluna "Elevação" no drill-down → FEITO na S15 (fdac345).
(b-extra) StatsCards usa formatElevation → FEITO na S15 (4cfd099).
(c) decisão dos enums documentada → FEITO na S15 (d7d756e).
Bônus S15: pace médio no drill-down (053239c), migração fitdecode
(3cf7668).

A ROTA A+ ESTÁ ENCERRADA. Próximos passos exigem ESCOLHA entre:

ROTA A+ — resíduos de baixo risco (ganho marginal hoje)
a) Remover bboxToOsmTileUrl (deprecated, sem uso). Commit pequeno.
b) RouteMap com React.lazy() — prepara terreno para segundo uso.
c) Cheat sheet de endpoints num futuro README (seção 4 já cobre).
Recomendação: só (a) vale a pena; (b) e (c) ficam para quando houver
demanda real.

ROTA B — feature nova (requer escolha com o usuário)
Escopo médio-grande. Exemplos:

    Stats "públicas" em perfis de terceiros (com privacidade via follow).
    Backend: novos endpoints com user_id + regra de follow.

    Comparação "este período vs. anterior" em cada gráfico.
    Backend: adicionar campos *_previous em StatsWeeklyResponse/
    StatsMonthlyResponse (mexe em contrato — decidir antes).

    Filtro de período no drill-down por tipo (90d, 1a, all).
    Backend: novo param em /stats/by-type.

    Export de atividades (CSV/GPX). Fora do escopo mobile/web atual.
    Requer: desenhar contrato + schema + teste (validável localmente, com
    pytest verde) + UI no front.

RECOMENDAÇÃO PARA A SESSÃO 17:
Começar pela Rota A+ (a) — remover bboxToOsmTileUrl (commit
pequeno, fecha a dívida deixada na S16). Em seguida, ESCOLHER entre
Rota A+ resíduos (b)/(c) e Rota B. Se o usuário preferir feature nova,
Rota B é viável — mas o assistente deve explicitar que está adiando
dívidas menores.

Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes do
fim, parar e entregar o HANDOFF completo da Sessão 17 neste mesmo
formato (seções 0 a 8).