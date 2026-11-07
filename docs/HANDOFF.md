HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 17

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

    IMPORTANTE — usuário NÃO tem ambiente local rodando. O fluxo de
    desenvolvimento é: editar em D:\Rumo, rodar pytest localmente (Docker de
    teste na 5433), commitar, push, Render + Vercel redeployam automaticamente,
    validar via HTTP em produção. Não presumir que o usuário vai "rodar o app
    localmente" para testar UI.

    DOCKER: INSTALADO E FUNCIONAL no Windows local. pytest -q local verde
    (124 passed ao fim da Sessão 17). Container de teste rumo_postgres_test
    na porta 5433. Para reativar numa sessão nova: (1) abrir Docker Desktop e
    esperar a baleia verde; (2) garantir que o terminal foi aberto via Win+R
    (fora do VS Code / Windows Terminal, que herdam PATH antigo);
    (3) cd D:\Rumo\backend; (4) docker compose -f docker-compose.test.yml up -d;
    (5) ..venv\Scripts\Activate.ps1 (pular se o prompt já mostra (.venv));
    (6) pytest -q.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada na Sessão 17:

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
│ │ ├── schemas\ # activity.py, like.py, stats.py, ...
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
│ # photos.ts, social.ts, stats.ts
├── assets
├── components\ # ActivityCard, ActivityResults, AppHeader,
│ # CommentsSection, LikeButton, NotificationBell,
│ # PeriodChart (unifica 4 gráficos), PhotoGallery,
│ # PhotoUpload, ProtectedRoute, RouteMap, StatsCards,
│ # UserResults
├── contexts
├── hooks\ # useActivities, useActivitySearch, useAuth, useDebounce,
│ # useNotifications, usePhotos, useProfile, useSocial,
│ # useStats, useUserSearch
├── lib\ # format.ts (format* + formatElevation),
│ # geo.ts (bboxToOsmTileGrid — único helper geo desde S17)
├── pages\ # ActivitiesPage, ActivityDetailPage, FeedPage,
│ # LoginPage, NotificationsPage, ProfilePage,
│ # RegisterPage, SearchPage, UploadPage
└── types\ # api.ts (todos os tipos, StatsByType* — S14)

DIVERGÊNCIAS vs handoff da Sessão 16:

    web/src/lib/geo.ts: bboxToOsmTileUrl REMOVIDA na S17. Restou só
    bboxToOsmTileGrid (mosaico 2×2). Commit 0f1c6ef.

    backend/app/routers/activities.py: rota /stats/by-type ganhou param
    `period: Literal["all", "90d", "1y"] = Query(default="all")` — S17.

    backend/app/services/stats_service.py: get_by_type ganhou param `period`
    e helper _apply_period_filter; get_summary e get_period_stats intocados.

    backend/tests/test_stats.py: +6 testes novos de period (service + rota).
    Total: 124 passed (era 118).

    web/src/api/stats.ts: +tipo StatsPeriod; getStatsByType(period = "all")
    sempre envia param explícito na URL.

    web/src/hooks/useStats.ts: statsKeys.byType(period); useStatsByType
    (period = "all", enabled = true).

    web/src/pages/ProfilePage.tsx: +useState<StatsPeriod>("all") e segmented
    control Todos/90 dias/1 ano no header do card "Por tipo de atividade".
    +import type { StatsPeriod }. +const PERIOD_FILTERS.

    web/src/components/StatsCards.tsx: INTOCADO na S17 (5 cards de summary
    continuam "todos os tempos", filtro é só na tabela por tipo).

    mobile/: INTOCADO desde a S11 (sem drill-down de stats no app).

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

        ..venv\Scripts\Activate.ps1
        ATENÇÃO: se o prompt já mostra (.venv), PULE o Activate —
        rodar ..venv\Scripts\Activate.ps1 com o venv já ativo dá
        "módulo '..venv' não encontrado" (inofensivo, mas confunde).

        pytest -q — esperado: 124 passed, 0 warnings (verde na Sessão 17)

    Se Activate.ps1 der erro de política:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

COMO TESTAR O BACKEND DE PRODUÇÃO SEM O APP (PowerShell)

    Login (retorna JWT):
    $body = "username=prod@rumo.com&password=senha12345"
    $login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
    $token = $login.access_token

    Stats by-type (S17 — validado em produção, 422 em valor inválido):
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=all"  -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=90d"  -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=1y"   -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3

    Detecção de versão em produção (S17 — como saber se o Render
    redeployou o commit mais recente):
    try {
        Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=30d" -Headers @{ Authorization = "Bearer $token" }
        Write-Host "RESULTADO: 200 — backend antigo (Sessao 17 NAO deployada)"
    } catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 422) {
            Write-Host "RESULTADO: 422 — backend NOVO no ar"
        }
    }

    Conta de teste: prod@rumo.com / senha12345.
    NOTA — essa conta tem 6 atividades (other: 3, walk: 3), todas com
    menos de 90 dias. Por isso period=all, period=90d e period=1y
    retornam IGUAIS para essa conta. NÃO é bug — é ausência de dado
    antigo. Os 124 testes locais (com _dt_ago(100) e _dt_ago(400))
    provam o filtro real. NÃO PERDER TEMPO achando que está quebrado.

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

    ATENÇÃO (S17 — NOVO) — arquivo "salvo" que não salvou. A S17 perdeu
    dois rounds porque o usuário colou o conteúdo novo no chat, mas o
    Ctrl+S não foi feito (ou foi feito em outro buffer/arquivo). SINTOMA:
    build ou pytest falha dizendo que um símbolo novo não existe, mesmo
    o assistente tendo entregado o arquivo. DIAGNÓSTICO RÁPIDO:
    Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>"
    Se não aparecer, o arquivo no disco ainda é o antigo. Pedir pro
    usuário salvar de novo. Isso NÃO é bug de código — é save perdido.
    REGRA: depois de entregar um arquivo que muda contrato, pedir a
    confirmação com Get-Content | Select-String ANTES de rodar build/test.

    ATENÇÃO — git diff pipeado no PowerShell pode exibir acentos como
    mojibake. É artefato de codepage do pipe, NÃO corrupção do arquivo.

    ATENÇÃO — git log --oneline no PowerShell às vezes cola a última linha
    com o prompt seguinte. Não é corrupção; é formatação.

    ATENÇÃO — git log sem --no-pager abre o less e trava o terminal.
    SEMPRE usar git --no-pager log ... ou prefixar com $env:PAGER="".

ACORDOS DE TRABALHO (válidos em todas as sessões)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão
    pendente, executar a recomendada salvo instrução explícita em contrário.
    (Usuário reforçou isso no início da Sessão 15, de novo na Sessão 16,
    e de novo na Sessão 17: "sempre vamos fazer o que você recomenda".)

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
    o próximo — reduz superfície de erro. Exceção legítima: 2 arquivos
    acoplados por mudança de contrato interno (ex.: hook + consumidor do hook).
    Nesse caso, entregar os 2 juntos e rodar 1 build.

    VERIFICAR SAVE ANTES DE BUILD: quando o assistente entrega um arquivo
    com símbolo novo (tipo, função, param), pedir ao usuário:
    Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>"
    antes de rodar build/test. A S17 mostrou que o Ctrl+S pode não pegar.

===============================================================================

    TL;DR PARA QUEM CHEGA AGORA
    ===============================================================================

    Backend: 124 testes passando LOCALMENTE (pytest -q verde na Sessão 17),
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
        GET /activities/stats/by-type?period=<all|90d|1y> — StatsByTypeResponse.
            (S17) period é opcional, default "all". Valores inválidos → 422.
            Janela é retroativa a partir de now() (started_at >= now() - N dias).

    Os 3 primeiros endpoints de stats (summary/weekly/monthly) aceitam
    activity_type opcional. O by-type NÃO aceita activity_type (é o
    drill-down por tipo — filtrar por tipo derrotaria o propósito).

    Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet
    (RouteMap no detalhe) + recharts (gráficos no perfil). Drill-down por
    tipo ganhou segmented control de janela temporal (S17).

    Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
    alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds.
    Sem drill-down de stats no app.

    [Sessão 17 — entregas]

        Backend — filtro de período no drill-down por tipo.

            routers/activities.py: /stats/by-type ganhou
            period: Literal["all","90d","1y"] = Query(default="all").
            Validação automática via FastAPI → 422 em valor inválido.

            services/stats_service.py: get_by_type(db, user_id, period="all").
            Novo helper _apply_period_filter(stmt, period) aplica
            WHERE started_at >= now() - INTERVAL para 90d/1y; no-op para all.
            get_summary e get_period_stats INTOCADOS.

            tests/test_stats.py: +6 testes (all baseline, 90d exclui antiga,
            1y exclui >365d, 1y superset de 90d, rota com param, rota com
            valor inválido → 422). Helper _dt_ago(days) para datas relativas
            a now(). Margem de 10 dias entre dentro/fora elimina flakiness.
            Total: 124 passed.

        Web — segmented control Todos / 90 dias / 1 ano.

            api/stats.ts: +tipo StatsPeriod = "all" | "90d" | "1y";
            getStatsByType(period="all") sempre envia ?period= na URL.

            hooks/useStats.ts: statsKeys.byType(period) inclui period na key
            (refetch automático); useStatsByType(period="all", enabled=true).

            pages/ProfilePage.tsx: +useState<StatsPeriod>("all") chamado
            byTypePeriod; segmented control no header do card da tabela
            (padrão inline-flex rounded-lg bg-gray-50 p-1 + botão
            rounded-md, coerente com os outros dois toggles da página).
            Call site: useStatsByType(byTypePeriod, isSelf).

            components/StatsCards.tsx: INTOCADO (summary de 5 cards é
            "todos os tempos", não faz parte do drill-down).

        Cleanup — bboxToOsmTileUrl removida (fecha dívida S16).

            web/src/lib/geo.ts: função deprecated removida. Restou só
            bboxToOsmTileGrid (mosaico 2×2). Build provou que ninguém
            importava (hash e tamanho do bundle idênticos antes/depois).
            Commit 0f1c6ef.

        Estado final: working tree limpo, HEAD == origin/main == 5925a03,
        pytest 124 passed / 0 warnings (local), npm run build verde
        (824 modules, ProfilePage +600 B), Render deployado (422 em
        period=30d validado em produção), Vercel redeployado (timing
        pós-push), flutter analyze sem issues (S16).

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

    Git (estado ao fim da Sessão 17):
    5925a03 (HEAD -> main, origin/main) feat(stats): filtro de periodo no drill-down por tipo (90d|1y|all)
    0f1c6ef chore(web): remove bboxToOsmTileUrl deprecated da Sessao 16
    1ab793d docs: handoff da Sessão 16
    a8a515f feat(web): miniatura do feed em mosaico 2x2 de tiles OSM
    05185f0 docs: handoff da Sessão 15
    4cfd099 refactor(web): StatsCards usa formatElevation em vez de inline
    fdac345 feat(web): coluna de elevacao no drill-down por tipo
    3cf7668 refactor(backend): migra parsing de .FIT de fitparse para fitdecode

    Todos os commits estão em origin/main (pushados).

    Render e Vercel deployam automático a cada push em main. A Sessão 17
    está deployada em produção (validado via 422 em period=30d).

===============================================================================

    O QUE FOI FEITO NA SESSÃO 17
    ===============================================================================

3.1 Validação de estado inicial (Sessão 17)

    PowerShell via Win+R, repo em D:\Rumo, venv backend ativo.

    git push: Everything up-to-date.

    HEAD == origin/main == 1ab793d (commit do handoff da S16).

    git status --short: limpo.

    npm run build: 824 modules, 1.80s, verde.

    flutter analyze: No issues found (2.9s).

    docker compose -f docker-compose.test.yml up -d: rumo_postgres_test
    já up (Running).

    pytest -q: 124 passed (na verdade 118 passed — a S17 ainda não tinha
    começado; 124 veio depois dos testes novos). 0 warnings.

    Descoberta de estrutura via Get-ChildItem: bate com o handoff da S16,
    sem divergências.

3.2 [Web] Rota A+ (a) — remover bboxToOsmTileUrl

    Lido web/src/lib/geo.ts.

    Função bboxToOsmTileUrl estava @deprecated desde a S16, sem uso
    (tree-shaking já tinha eliminado do bundle).

    Entrega: geo.ts completo sem a função, com nota [Sessão 17]
    registrando a remoção.

    npm run build: 824 modules, 1.99s, verde. HASH E TAMANHO de
    index-*.js IDÊNTICOS antes/depois — prova que a função era 100% morta.

    Commit: 0f1c6ef. Push OK.

3.3 [Backend + Web] Rota B — filtro de período no drill-down por tipo

    Decisão de contrato (aprovada pelo usuário com "sempre vamos fazer o
    que você recomenda"):

        Param: period, tipo Literal["all","90d","1y"], default "all".
        "1y" = 365 dias corridos.
        Web: 3 botões (Todos / 90 dias / 1 ano), default "Todos".
        Mobile: fora do escopo (não tem drill-down).
        4-6 testes novos, sem tocar nos 118 existentes.

    Entrega 1/4 — backend/app/routers/activities.py.

        Import novo: from typing import Literal.
        stats_by_type ganhou period: Literal[...] = Query(default="all", ...).
        Docstring atualizada. Chamada stats_service.get_by_type(db, uid, period).

    Entrega 2/4 — backend/app/services/stats_service.py.

        Imports novos: from datetime import timedelta; from typing import Literal.
        Novo helper _apply_period_filter(stmt, period) — espelha o estilo de
        _apply_type_filter. Aplica Activity.started_at >= func.now() - timedelta
        para 90d/1y; no-op para all.
        get_by_type(db, user_id, period="all") — stmt = _apply_period_filter
        (stmt, period) antes do GROUP BY.
        get_summary e get_period_stats intocados.

        pytest -q após o service: 118 passed (testes antigos não quebraram
        porque default "all" preserva assinatura).

    Entrega 3/4 — backend/tests/test_stats.py.

        +helper _dt_ago(days) (relativo a now(), documentado).
        +6 testes: all baseline, 90d exclui antiga, 1y exclui >365d,
        1y superset de 90d, rota com param, rota com valor inválido → 422.
        Nenhum teste antigo alterado.

        pytest -q: 124 passed em 32.91s. 0 warnings.

    Entrega 4/4 — web (api/stats.ts + hooks/useStats.ts + pages/ProfilePage.tsx).

        api/stats.ts: +tipo StatsPeriod; getStatsByType(period="all")
        com URLSearchParams sempre enviando ?period=.

        hooks/useStats.ts: +import StatsPeriod; statsKeys.byType(period) =
        ["stats","by-type",period]; useStatsByType(period="all",
        enabled=true); queryFn chama getStatsByType(period).

        pages/ProfilePage.tsx: +import type { StatsPeriod }; +const
        PERIOD_FILTERS; +useState<StatsPeriod>("all") byTypePeriod;
        call site virou useStatsByType(byTypePeriod, isSelf); header do
        card da tabela ganhou segmented control (Todos/90 dias/1 ano)
        com justify-between.

        StatsCards.tsx: INTOCADO.

    Dois rounds perdidos com "arquivo salvo que não salvou":

        Round 1: build falhou em useStats.ts (TS2305: StatsPeriod não
        existe em ../api/stats). Diagnóstico: api/stats.ts no disco era
        o antigo. Salvamento não pegou.

        Round 2: build falhou em ProfilePage.tsx (TS2345: boolean não é
        StatsPeriod). Diagnóstico: ProfilePage.tsx no disco era o antigo.
        Salvamento não pegou.

        Ambos resolvidos pedindo Get-Content | Select-String para
        confirmar o save antes do build. Lição registrada em "ATENÇÃO
        (S17) — arquivo salvo que não salvou" na seção 0.

    npm run build final: 824 modules, 2.42s, verde. ProfilePage-*.js
    cresceu de 14.35 kB para 14.95 kB (+600 B). index-*.js mesmo tamanho
    (nada novo entrou no chunk principal).

    Commit: 5925a03. Push OK. Render + Vercel redeployaram.

    Validação em produção:

        period=all: 200 (shape antigo, retrocompatível).
        period=90d: 200 (mesmo retorno que all — conta de teste sem
                        atividade >90d; não é bug).
        period=1y:  200 (idem).
        period=30d: 422 — CONFIRMADO. Backend novo em produção.

3.4 Estado final da sessão

    Working tree limpo, main == origin/main == 5925a03.

    npm run build: verde (824 modules).

    pytest -q: 124 passed, 0 warnings (local).

    Backend em produção: 422 em period=30d (Sessão 17 deployada).

    flutter analyze: No issues found (não tocado na S17; S16 já estava ok).

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

    GET /activities/stats/by-type?period=<all|90d|1y> (S17 — period opcional)
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
    period: "all" (default) | "90d" | "1y". Valores inválidos → 422.
    Janela é retroativa: started_at >= now() - (90d | 365d).

    Todos os endpoints de stats são do current_user (não aceitam user_id).
    A UI só mostra stats no próprio perfil (isSelf).

===============================================================================

    COMMITS PENDENTES / ESTADO DO REPO
    ===============================================================================

    Sessões 9 a 17 commitadas e pushadas.

    origin/main == main == HEAD == 5925a03.

    Sessão 17 fechada com este handoff (commit docs: handoff da Sessão 17).

    Nenhuma pendência conhecida de git.

===============================================================================

    SCRIPTS ÚTEIS (PowerShell)
    ===============================================================================

[Sessão 18 — primeira ação] Abrir PowerShell via Win+R → "powershell"
(NÃO abrir de dentro do VS Code / Windows Terminal)
Depois:
[Sessão 18 — primeira ação] Estado do repo (sem abrir o less)

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short
[Sessão 18 — primeira ação] Descoberta da estrutura do repo

Get-ChildItem -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app\routers -File | Select-Object Name
Get-ChildItem D:\Rumo\backend\tests -File | Select-Object Name
[Sessão 18 — primeira ação] Sanidade de build

cd D:\Rumo\web
npm run build

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
[Sessão 18 — primeira ação] Docker + pytest local

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps
# Se o prompt já mostra (.venv), PULE a linha abaixo.
..venv\Scripts\Activate.ps1
pytest -q
Verificar que fitdecode está instalado e fitparse NÃO

python -c "import fitdecode; print('fitdecode OK:', fitdecode.version)"
python -c "import fitparse" 2>&1 # esperado: ModuleNotFoundError
[Sessão 18 — primeira ação] Detecção de versão em produção (backend novo?)

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
try {
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=30d" -Headers @{ Authorization = "Bearer $token" }
    Write-Host "RESULTADO: 200 — backend AINDA é o antigo"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 422) {
        Write-Host "RESULTADO: 422 — backend NOVO no ar (S17 deployada)"
    } else {
        Write-Host "RESULTADO: erro inesperado: $($_.Exception.Response.StatusCode.value__)"
    }
}
Login (produção)

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
Feed com bbox (produção)

$feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=5" -Headers @{ Authorization = "Bearer $token" }
$feed | ForEach-Object { "$($_.id.Substring(0,8))  $($_.title)  bbox=$($_.bbox -join ',')" }
Stats (produção)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/monthly?months=6" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=all" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Track (produção)

$t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/<id>/track" -Headers @{ Authorization = "Bearer $token" }
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

    (NOVA — Sessão 17) Filtro `period` usa `now()` do Postgres.
    A janela retroativa é calculada com `func.now() - timedelta(...)` — ou
    seja, o relógio de referência é o do servidor de banco, não o do
    processo Python. Para o usuário final, é o comportamento correto (o
    que importa é "agora" na hora da query). Mas isso significa que testes
    determinísticos com `_dt(2026, 1, 5)` NÃO servem para testar `period`
    — precisam usar datas relativas a `now()`. Foi por isso que a S17
    adicionou `_dt_ago(days)` no test_stats.py. REGRA: qualquer teste de
    `period` (ou de outra feature baseada em `now()`) DEVE usar
    `datetime.now(timezone.utc) - timedelta(days=N)` com margem ≥ 10 dias
    entre dentro e fora da janela. Não misturar com `_dt` fixo.

    (NOVA — Sessão 17) `StatsCards.tsx` mostra summary "todos os tempos",
    não filtrado por `period`. O segmented control de período afeta
    APENAS a tabela por tipo. Isso é intencional — summary é "totais
    gerais" e fica no topo da página; a tabela é drill-down. Se um dia o
    usuário quiser filtro no summary, é feature nova (não extensão da S17).

    (NOVA — Sessão 17) Conta `prod@rumo.com` sem atividades com mais de
    90 dias. Por isso `period=all`, `period=90d` e `period=1y` retornam
    IGUAIS em produção. Para testar o filtro em produção com diferença
    visível, seria preciso (a) upload de GPX com data no passado, ou
    (b) aceitar os 124 testes locais como prova (recomendado — são mais
    fortes que qualquer teste de produção nessa conta). NÃO PERDER TEMPO
    achando que está quebrado.

    (Oportunidade) RouteMap.tsx é reutilizável em qualquer página que
    renderize uma rota. Hoje só é usado em ActivityDetailPage. Se aparecer
    um segundo uso, considerar React.lazy() para tirar o leaflet (163.60 kB)
    do chunk da página que não mostra mapa. Ganho hoje é marginal.

    (Oportunidade) Drill-down de stats por tipo poderia ganhar:
        - Comparação "este período vs. anterior" (ex.: 90d vs. os 90d
          anteriores). Backend: adicionar campos *_previous em
          StatsByTypeResponse ou em StatsWeeklyResponse/MonthlyResponse
          (mexe em contrato — decidir antes).
        - Filtro de período custom (ex.: "últimos 180 dias"). Hoje é
          all|90d|1y fixo. Se virar requisito, o param `period` pode
          ganhar mais valores (aditivo, sem quebrar).

    (Oportunidade) Stats no perfil: /activities/stats/summary, /weekly,
    /monthly e /by-type são só do current_user. Se um dia o requisito for
    "ver stats de outro usuário", precisa de novos endpoints (com
    privacidade, provavelmente via follow).

    (Oportunidade) Export de atividades (CSV/GPX). Fora do escopo atual.
    Requer: desenhar contrato + schema + teste + UI no front.

    Mobile: sem inclinação/rotação 3D (flutter_map é 2D). Se 3D for
    requisito, avaliar maplibre_gl (decisão maior, pesada).

    TimeoutException do app mobile não reproduzido desde a Sessão 9.
    Registrar se voltar (tela + log do flutter run).

===============================================================================

    PRÓXIMOS PASSOS RECOMENDADOS (Sessão 18 e além)
    ===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 18 (antes de qualquer mudança de código):

    No terminal (PowerShell via Win+R → "powershell"):
    cd D:\Rumo
    git push
    git --no-pager log --oneline -8
    git status --short
    cd web ; npm run build
    cd ..\mobile
    & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
    Confirmar: push aceito, HEAD == origin/main == 5925a03 (ou o commit do
    handoff), build e analyze verdes, working tree limpo.

    DOCKER + PYTEST LOCAL:
    docker version
    docker compose version
    cd D:\Rumo\backend
    docker compose -f docker-compose.test.yml up -d
    docker ps
    # Se prompt já mostra (.venv), pular:
    ..venv\Scripts\Activate.ps1
    pytest -q
    Esperado: 124 passed, 0 warnings.

    DETECÇÃO DE VERSÃO EM PRODUÇÃO (para saber se o Render está no
    commit mais recente):
    Rodar o try/catch da seção 6 ("Detecção de versão em produção").
    Esperado: 422 em period=30d.

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

ESTADO DA ROTA B (Sessão 17): PRIMEIRO ITEM FECHADO.
Filtro de período no drill-down por tipo → FEITO e em produção (5925a03).
Backend: /stats/by-type?period=all|90d|1y, default all, 422 em valor
inválido. Web: segmented control no ProfilePage. StatsCards e mobile
intocados.

A ROTA B SEGUE ABERTA para os demais itens. Próximos passos exigem
ESCOLHA entre:

OPÇÃO 1 — Comparação "este período vs. anterior".
    Backend: adicionar campos *_previous em StatsWeeklyResponse e
    StatsMonthlyResponse (ou novo endpoint /stats/compare).
    MEXE EM CONTRATO — decidir antes de codar (nomes dos campos,
    semântica de "anterior" — janela imediatamente anterior? mesmo
    período do ano passado?).
    Front: UI de comparação nos gráficos (delta numérico, cor, etc).

OPÇÃO 2 — Stats públicas em perfis de terceiros.
    Backend: novos endpoints com user_id + regra de follow.
    Escopo médio-grande. Define privacidade.

OPÇÃO 3 — Export de atividades (CSV/GPX).
    Escopo maior. Desenhar contrato + schema + teste + UI.
    GPX já existe no backend (gpx_service.py) — provavelmente
    reutilizável. CSV é mais simples (Excel/Sheets).

OPÇÃO 4 — Resíduos de baixo risco da Rota A+ (b)/(c).
    (b) RouteMap com React.lazy() — prepara terreno para segundo uso.
    (c) Cheat sheet de endpoints num README.
    Ganho marginal. Recomendação: só se não houver Rota B clara.

RECOMENDAÇÃO PARA A SESSÃO 18:

Antes de escolher, VALIDAR ESTADO (seção 6 — primeira ação). Se estiver
tudo verde (build, analyze, pytest 124, 422 em produção), aí escolher.

Se a escolha for Rota B, minha recomendação é OPÇÃO 1 (comparação
período vs. anterior) pelos motivos:

  - É a evolução natural do que a S17 entregou (já temos `period`
    funcionando; comparar é o próximo passo lógico).
  - Não exige novo endpoint nem regra de privacidade — só estende o
    response existente com dados já computáveis.
  - Valida 100% localmente com pytest.
  - Front: 1 componente (gráfico de barras com delta) — escopo contido.

MAS: é mudança de contrato. A primeira coisa a fazer, antes de codar,
é DEFINIR o contrato exato: nome dos campos (`*_previous`? objeto
`previous`?), semântica de "anterior" (janela imediatamente anterior
vs. mesmo período do ano anterior), e como a UI mostra (delta absoluto?
percentual? ambos?). Recomendo "janela imediatamente anterior"
(mais intuitivo: "esta semana vs. semana passada"). A Sessão 18 deve
gastar os primeiros 5-10% do contexto definindo isso com o usuário
e só então codar.

Se a escolha for Opção 2 ou 3, o assistente deve explicitamente dizer
que está adiando a Opção 1 (mais barata e natural agora).

Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes
do fim, parar e entregar o HANDOFF completo da Sessão 18 neste mesmo
formato (seções 0 a 8).