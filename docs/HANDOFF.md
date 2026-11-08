HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 19

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
    (136 passed ao fim da Sessão 19). Container de teste rumo_postgres_test
    na porta 5433. Para reativar numa sessão nova:
    (1) abrir Docker Desktop e esperar a baleia verde;
    (2) garantir que o terminal foi aberto via Win+R (fora do VS Code /
        Windows Terminal, que herdam PATH antigo);
    (3) cd D:\Rumo\backend;
    (4) docker compose -f docker-compose.test.yml up -d;
    (5) .\venv\Scripts\Activate.ps1  (UM ponto, não dois — ver lição S19);
    (6) python -m pytest -q  (ou pytest -q, se o PATH do venv estiver certo).

    VENV: ao fim da S19, o venv ativo é D:\Rumo\backend\venv (sem ponto),
    criado com Python 3.13.7. Havia também um .venv antigo (não removido —
    ver dívida técnica) que NÃO deve ser usado.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada na Sessão 19:

D:\Rumo
├── .vscode
├── backend
│ ├── .pytest_cache
│ ├── .ruff_cache
│ ├── .venv\                # ANTIGA, não usar; remoção pendente (dívida)
│ ├── venv\                 # ATIVA (Python 3.13.7) — usar esta
│ ├── alembic
│ ├── app
│ │ ├── core
│ │ ├── models
│ │ ├── routers\            # activities.py, auth.py, comments.py, feed.py,
│ │ │                       # notifications.py, photos.py, users.py, __init__.py
│ │ ├── schemas\            # activity.py, like.py, stats.py, user.py, ...
│ │ ├── services\           # activity_service.py, comment_service.py, errors.py,
│ │ │                       # feed_service.py, fit_service.py, follow_service.py,
│ │ │                       # gpx_service.py, like_service.py, notification_service.py,
│ │ │                       # photo_service.py, stats_service.py, user_service.py
│ │ └── __pycache__
│ ├── samples
│ ├── scripts
│ ├── tests\                # conftest.py + test_calories.py + test_comment.py +
│ │                         # test_follow.py + test_like.py + test_stats.py + __init__.py
│ ├── _scratch
│ ├── docker-compose.test.yml
│ ├── pytest.ini
│ └── requirements.txt
├── docs
│ └── HANDOFF.md            # este arquivo
├── mobile
│ └── lib
│ ├── models\               # activity.dart, activity_track.dart, comment.dart
│ ├── pages\                # activity_detail_page.dart, feed_page.dart, login_page.dart
│ ├── services
│ └── widgets\              # activity_map.dart, like_button.dart
└── web
    └── src
        ├── api\            # activities.ts, auth.ts, client.ts, notifications.ts,
        │                   # photos.ts, social.ts, stats.ts
        ├── assets
        ├── components\     # ActivityCard, ActivityResults, AppHeader, CommentsSection,
        │                   # LikeButton, NotificationBell, PeriodChart, PhotoGallery,
        │                   # PhotoUpload, ProtectedRoute, RouteMap, StatsCards, UserResults
        ├── contexts
        ├── hooks\          # useActivities, useActivitySearch, useAuth, useDebounce,
        │                   # useNotifications, usePhotos, useProfile, useSocial,
        │                   # useStats, useUserSearch
        ├── lib\            # format.ts, geo.ts
        ├── pages\          # ActivitiesPage, ActivityDetailPage, FeedPage, LoginPage,
        │                   # NotificationsPage, ProfilePage, RegisterPage, SearchPage, UploadPage
        └── types\          # api.ts

DIVERGÊNCIAS vs handoff da Sessão 18:

    backend/app/routers/users.py: +4 endpoints GET /users/{user_id}/stats/{summary,
        weekly, monthly, by-type}. +helper _ensure_can_view_stats (404 target
        inexistente; 403 viewer não segue; self sempre OK). Endpoints declarados
        ANTES de @router.get("/{user_id}") para não colidir com parsing de UUID.
        Reaproveitam 100% do stats_service (mesmas assinaturas, só passam
        target_id). Sem mudança em /activities/stats/*.

    backend/tests/test_stats.py: +7 testes de stats públicas (self OK, 403 sem
        follow, 200 com follow, weekly shape, monthly 403, by-type com previous,
        user inexistente 404). +helpers _make_follow e _client_as (client com
        override local de get_current_user, sem tocar no conftest). Total:
        136 passed (era 129 na S18).

    web/src/api/stats.ts: +4 funções getUserStats{Summary,Weekly,Monthly,ByType}
        (mesmo shape, path /users/{userId}/stats/*). As 4 originais intocadas.

    web/src/hooks/useStats.ts: +statsKeys.user{All,Summary,Weekly,Monthly,ByType}
        (namespaced por userId) +4 hooks useUserStats{...} com param canView
        (enabled = canView && !!userId). Os 4 hooks originais intocados.

    web/src/pages/ProfilePage.tsx: +import dos 4 hooks novos; +canView =
        isSelf || isFollowing; +showOtherStats = !isSelf && isFollowing;
        +8 chamadas de hook (4 self + 4 user) com enabled complementar;
        +seleção de fonte (isSelf ? self : user); +seção de stats passa de
        {isSelf && ...} para {canView && ...}. Conteúdo interno intocado.

    mobile/: INTOCADO desde a S11.

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

COMO RODAR DOCKER E PYTEST LOCAL (Windows deste usuário)

    Docker Desktop instalado em:
    C:\Users\nasci\AppData\Local\Programs\DockerDesktop
    docker.exe em:
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
        .\venv\Scripts\Activate.ps1     # UM ponto, NÃO dois
        # ATENÇÃO: se o prompt já mostra (venv), PULE o Activate —
        # rodar .\venv\Scripts\Activate.ps1 com o venv já ativo é inofensivo,
        # mas confunde. Se der "módulo '..venv' não encontrado", você digitou
        # dois pontos por engano (ver lição S19).
        python -m pytest -q — esperado: 136 passed, 0 warnings

    Se Activate.ps1 der erro de política:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

    ⚠️ LIÇÃO S19 — PYTHON 3.14 NÃO SERVE PARA ESTE PROJETO.
    O `py -3` deste Windows aponta para Python 3.14
    (C:\Users\nasci\AppData\Local\Programs\Python\Python314). As versões
    fixadas no requirements.txt (pydantic 2.10.4 → pydantic-core 2.27.2,
    asyncpg 0.30.0, greenlet 3.1.1) NÃO têm wheels cp314 — o pip tenta
    compilar do zero e falha (PyO3 0.22.6 não suporta 3.14; asyncpg/greenlet
    quebram no compilador C com a API nova).
    Pythons instalados (confirmado com `py -0p` na S19):
        3.14 (default do `py -3`) — NÃO USAR
        3.13 (C:\Python313)       — USAR ESTE
        3.11 (C:\Python311)       — alternativa, mas não testado na S19
        (não há 3.12)
    Criar venv correto:
        py -3.13 -m venv D:\Rumo\backend\venv
    Se `py -3.13 -m venv` falhar, usar caminho direto:
        C:\Python313\python.exe -m venv D:\Rumo\backend\venv
    Se o prompt mostrar (venv) apontando para pasta apagada (venv fantasma),
    rodar `deactivate` ANTES de recriar — senão o prompt continua enganando.

COMO TESTAR O BACKEND DE PRODUÇÃO SEM O APP (PowerShell)

    Login (retorna JWT):
    $body = "username=prod@rumo.com&password=senha12345"
    $login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
    $token = $login.access_token

    ⚠️ LIÇÃO S19 — "QUEM SOU EU" É GET /auth/me, NÃO /users/me.
    /users/me devolve 422 (FastAPI tenta parsear "me" como UUID).
    Endpoint correto:
    $me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
    $meId = $me.id
    (fallback: decodificar o `sub` do JWT — payload base64url.)

    Stats de terceiros (S19 — validado em produção):
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/monthly?months=6" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

    Conta de teste: prod@rumo.com / senha12345.
    id de prod: 01a12c83-be2a-71fa-b966-1c93ca64f341 (6 atividades).
    prod segue Prod2 (id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades).
    Use Prod2 para validar o cenário "terceiro seguido" (os números de
    Prod2 são bem distintos dos de prod — 2 vs 6 atividades, 14.643 m vs
    26.443 m — qualquer vazamento é óbvio).
    Para o cenário "terceiro NÃO seguido", usar a busca
    (/users/search?q=a) e escolher um id que não seja prod nem Prod2.

    ⚠️ LIÇÃO S18/S19 — "422 de versão" NÃO distingue S17 de S18.
    O endpoint /activities/stats/by-type?period=30d devolve 422 desde a S17.
    Para saber se o Render redeployou a S18, o check correto é GET ?period=90d
    e verificar se o item tem a CHAVE "previous" (valor null é OK). Para a S19,
    o check é: GET /users/{meId}/stats/summary responde 200 (não 404) e
    GET /users/me responde 422 (esse endpoint nunca existiu — 404 aqui seria
    sinal de que o router de users está quebrado). NÃO confundir "backend de
    pé" com "versão certa no ar".

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

    ATENÇÃO (S17, reforçada na S19) — arquivo "salvo" que não salvou.
    SINTOMA: build ou pytest falha dizendo que um símbolo novo não existe,
    mesmo o assistente tendo entregado o arquivo. DIAGNÓSTICO RÁPIDO:
    Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>"
    Se não aparecer, o arquivo no disco ainda é o antigo. Pedir pro
    usuário salvar de novo. Isso NÃO é bug de código — é save perdido.
    REGRA: depois de entregar um arquivo que muda contrato, pedir a
    confirmação com Get-Content | Select-String ANTES de rodar build/test.
    Na S19 isso funcionou nas duas entregas (backend users.py, front
    ProfilePage.tsx) — manter.

    ATENÇÃO — git diff pipeado no PowerShell pode exibir acentos como
    mojibake. É artefato de codepage do pipe, NÃO corrupção do arquivo.

    ATENÇÃO — git log --oneline no PowerShell às vezes cola a última linha
    com o prompt seguinte. Não é corrupção; é formatação.

    ATENÇÃO — git log sem --no-pager abre o less e trava o terminal.
    SEMPRE usar git --no-pager log ... ou prefixar com $env:PAGER="".

    ATENÇÃO (S19 — NOVO) — Pylance reclamando de "Não foi possível resolver
    a importação fastapi/sqlalchemy/pytest..." NÃO é erro de código.
    É o VS Code apontando para o interpretador errado (provavelmente o .venv
    antigo ou o Python global). Terminal está certo (venv). Correção:
    Ctrl+Shift+P → "Python: Select Interpreter" → escolher
    D:\Rumo\backend\venv\Scripts\python.exe → Developer: Reload Window.
    Se não aparecer, criar .vscode/settings.json com
    "python.defaultInterpreterPath": "D:\\Rumo\\backend\\venv\\Scripts\\python.exe"
    e "python.analysis.extraPaths": ["D:\\Rumo\\backend"].

ACORDOS DE TRABALHO (válidos em todas as sessões)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão
    pendente, executar a recomendada salvo instrução explícita em contrário.
    (Usuário reforçou isso no início das Sessões 15, 16, 17, 18 e 19.)

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
    antes de rodar build/test.

===============================================================================

    TL;DR PARA QUEM CHEGA AGORA
    ===============================================================================

    Backend: 136 testes passando LOCALMENTE (pytest -q verde na Sessão 19),
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
            (S17) period opcional, default "all". Inválidos → 422.
            (S18) cada item tem "previous" (janela imediatamente anterior)
            ou null (period="all" ou tipo ausente na janela anterior).

    [Sessão 19] Stats públicas em perfis de terceiros — 4 endpoints novos,
    espelhando os 4 acima, mas com user_id no path:

        GET /users/{user_id}/stats/summary   → StatsSummary
        GET /users/{user_id}/stats/weekly    → StatsWeeklyResponse
        GET /users/{user_id}/stats/monthly   → StatsMonthlyResponse
        GET /users/{user_id}/stats/by-type   → StatsByTypeResponse

    Regra de acesso (helper _ensure_can_view_stats em routers/users.py):
    - self (viewer == target) → 200, sem consulta extra.
    - viewer segue target       → 200.
    - viewer não segue target   → 403 ("Você precisa seguir este usuário pra
                                   ver as estatísticas dele").
    - target não existe         → 404 ("Usuário não encontrado") — 404, não
                                   403, para não vazar existência.
    Mesmo padrão do /activities/{id}/track e do feed. Reaproveitam 100% do
    stats_service (mesmas assinaturas, target_id no lugar de current_user.id).
    by-type mantém `previous` (mesma semântica da S18, custo zero).

    Os 3 primeiros endpoints de /activities/stats/* aceitam activity_type
    opcional. O by-type NÃO aceita (é o drill-down por tipo).

    Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet
    (RouteMap no detalhe) + recharts (gráficos no perfil). Drill-down por
    tipo tem segmented control de janela temporal (S17) e, quando period
    != "all", coluna "vs. anterior" com delta (Ativ./Dist./Elev.) colorido
    (S18). [S19] A seção de stats do ProfilePage agora renderiza também
    para perfis de terceiros quando o viewer segue o alvo; quando não segue,
    não renderiza.

    Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
    alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds.
    Sem drill-down de stats no app.

    [Sessão 19 — entregas]

        Backend — stats públicas em perfis de terceiros.

            routers/users.py: +4 endpoints GET /users/{user_id}/stats/{...},
            declarados ANTES de @router.get("/{user_id}") (senão FastAPI
            tenta parsear "stats" como UUID → 422). +helper
            _ensure_can_view_stats (self OK / segue OK / senão 403; target
            inexistente → 404). Reaproveitam stats_service.get_summary,
            get_period_stats e get_by_type sem mudança de assinatura.
            Imports novos: Literal (typing), StatsSummary/StatsWeeklyResponse/
            StatsMonthlyResponse/StatsByTypeResponse (schemas.stats),
            stats_service (services).

            tests/test_stats.py: +7 testes no fim do arquivo, seção
            "# ===== Stats públicas em perfis de terceiros [Sessão 19] =====".
            +helper _make_follow (insert direto de Follow, sem notificação).
            +helper _client_as(user, test_engine) — AsyncClient com override
            LOCAL de get_current_user (não toca no conftest; usa o test_engine
            session-scoped para o mesmo banco). Testes:
              - test_user_stats_summary_self_ok (regressão self, via client
                padrão)
              - test_user_stats_summary_forbidden_when_not_following (403,
                mensagem contém "seguir")
              - test_user_stats_summary_allowed_when_following (200, dados
                do ALVO — prova que target_id é respeitado)
              - test_user_stats_weekly_allowed_when_following (shape
                {weeks, items})
              - test_user_stats_monthly_forbidden_when_not_following (403)
              - test_user_stats_by_type_previous_when_following (200,
                previous preenchido para 90d)
              - test_user_stats_unknown_user_404 (404, não 403)
            Total: 136 passed.

        Web — stats no perfil de terceiros seguidos.

            api/stats.ts: +4 funções getUserStats{Summary,Weekly,Monthly,
            ByType} com userId no path. As 4 originais (getStatsSummary,
            getStatsWeekly, getStatsMonthly, getStatsByType) INTOCADAS,
            incluindo o docstring S18 do by-type.

            hooks/useStats.ts: +statsKeys.user{All,Summary,Weekly,Monthly,
            ByType} namespaced por userId (não colidem com as keys self).
            +4 hooks useUserStats{Summary,Weekly,Monthly,ByType}(userId |
            undefined, canView, ...). `enabled = canView && !!userId`;
            staleTime 60s; retry 1. Os 4 hooks originais INTOCADOS, incluindo
            os comentários S13/S14/S17/S18.

            pages/ProfilePage.tsx: +import dos 4 hooks novos; +canView =
            isSelf || isFollowing; +showOtherStats = !isSelf && isFollowing;
            +8 chamadas de hook (4 self + 4 user) com enabled complementar
            (self.enabled = isSelf...; user.enabled = showOtherStats...);
            +seleção de fonte (isSelf ? selfQuery : userQuery); +seção de
            stats passa de {isSelf && (...)} para {canView && (...)}.
            Conteúdo interno (TYPE_FILTERS, TYPE_LABELS, PACE_TYPES,
            PERIOD_FILTERS, toggles, StatsCards, PeriodChart, tabela,
            PreviousDelta, DeltaLine, lista de atividades, abas, UserRow,
            computePace) INTOCADO.

        Estado final: working tree limpo, HEAD == origin/main == 0df0b9f.
        pytest 136 passed / 0 warnings (local). ruff All checks passed.
        npm run build verde (824 modules, ProfilePage 17.52 kB).
        flutter analyze sem issues. Render deployado (endpoints S19
        respondendo em produção). Vercel redeployado e validado
        visualmente: cenário 1 (self, 6 atividades / 26.443 m) OK;
        cenário 2 (Prod2 seguido, 2 atividades / 14.643 m / 0 kcal / pace
        496,89 s/km) OK — dados do alvo, não vazaram os do viewer;
        cenário 3 (terceiro não seguido) OK — sem seção de stats.

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
    Python: 3.13.7 (venv em D:\Rumo\backend\venv) — NÃO usar 3.14
    Venv backend: D:\Rumo\backend\venv (ativa com .\venv\Scripts\Activate.ps1)

    Git (estado ao fim da Sessão 19):
    0df0b9f (HEAD -> main, origin/main) feat(web): stats no perfil de terceiros seguidos (Sessao 19)
    229e36b feat(users): stats publicas em perfis de terceiros (Sessao 19)
    4ba08da docs: handoff da Sessao 18
    b0e3a29 feat(stats): comparacao com janela anterior no drill-down por tipo (Sessao 18)
    494d8cc docs: handoff da Sessao 17
    5925a03 feat(stats): filtro de periodo no drill-down por tipo (90d|1y|all)
    0f1c6ef chore(web): remove bboxToOsmTileUrl deprecated da Sessao 16
    1ab793d docs: handoff da Sessão 16
    a8a515f feat(web): miniatura do feed em mosaico 2x2 de tiles OSM
    05185f0 docs: handoff da Sessão 15

    Todos os commits estão em origin/main (pushados).
    Render e Vercel deployam automático a cada push em main.

===============================================================================

    O QUE FOI FEITO NA SESSÃO 19
    ===============================================================================

3.1 Validação de estado inicial (Sessão 19)

    PowerShell via Win+R, repo em D:\Rumo.
    git push: Everything up-to-date.
    HEAD == origin/main == 4ba08da (handoff da S18 commitado).
    git status --short: limpo.
    npm run build: 824 modules, verde (ProfilePage 15.98 kB).
    flutter analyze: No issues found.
    docker version / compose version: OK.
    docker ps: rumo_postgres_test subiu na 5433.

    pytest -q: NÃO rodou de primeira — venv quebrado (ver 3.2).

3.2 Recuperação do venv (lição grande da S19)

    Sintoma 1: `..venv\Scripts\Activate.ps1` falhou com "Não foi possível
    carregar o módulo '..venv'". Causa: o handoff da S18 tinha o typo
    "..venv" (dois pontos) — o correto é ".\venv" (um ponto).

    Sintoma 2: o prompt mostrava (venv), mas D:\Rumo\backend\venv não
    existia — era um venv "fantasma" apontando para pasta apagada.
    Correção: `deactivate` antes de qualquer coisa.

    Sintoma 3: `py -3 -m venv venv` criou venv com Python 3.14 (default
    do `py -3`). `pip install -r requirements.txt` falhou compilando
    asyncpg, greenlet e pydantic-core — nenhuma tem wheel cp314.
    Diagnóstico: `py -0p` mostrou 3.14 (default), 3.13 (C:\Python313),
    3.11 (C:\Python311); sem 3.12.

    Correção final (funcionou):
        cd D:\Rumo\backend
        deactivate                      # se prompt mostrar (venv)
        Remove-Item -Recurse -Force .\venv   # remove o 3.14 quebrado
        py -3.13 -m venv D:\Rumo\backend\venv
        .\venv\Scripts\Activate.ps1     # UM ponto
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt   # baixa wheels, sem compilar
        python -m pytest -q             # 129 passed (estado da S18)

    Pytest: 129 passed in 34s. fitdecode 0.11.0 OK; fitparse ausente (correto).

    Detecção de versão em produção (S18): campo `previous` presente no
    period=90d → S18 no ar. Estrutura conferida via Get-ChildItem: igual
    ao handoff da S18, exceto que existem DUAS pastas de venv (.venv antiga
    e venv nova). ruff All checks passed.

3.3 Decisão de rota (Opção 2 — stats públicas)

    Usuário reforçou "sempre vamos fazer o que você recomendar".
    Opções do handoff da S18: (1) year-over-year, (2) stats públicas em
    perfis de terceiros, (3) export CSV/GPX, (4) resíduos de baixo risco.
    Recomendação: Opção 2. Motivos: evolução natural do produto (o app já
    mostra perfil de terceiros, mas esconde stats); adição de endpoints
    novos (não muda contrato existente); 100% testável local; front pequeno
    (1 condicional no ProfilePage); privacidade alinhada com /track e feed.

    Decisões travadas:
    - Regra de acesso: viewer segue o alvo (mesma do /track).
    - Endpoints novos /users/{user_id}/stats/* (não param em /activities).
    - by-type de terceiros mantém `previous`.
    - Front: se !isSelf && isFollowing → mostra stats do alvo; se não
      segue → não renderiza (sem mensagem "siga pra ver stats").

3.4 [Backend] Implementação + testes

    Ordem de entrega (uma versão por arquivo por resposta):
        users.py (completo)
        test_stats.py (completo)
    Cada um: usuário cola Get-Content -Encoding UTF8, assistente entrega
    arquivo completo, usuário confirma com Select-String, depois pytest.

    users.py:
        - +helper _ensure_can_view_stats(db, viewer_id, target_id):
          viewer == target → return; db.get(User, target_id) → 404 se None;
          is_following → 403 se False.
        - +4 endpoints declarados ANTES de @router.get("/{user_id}"):
          /{user_id}/stats/summary, /weekly, /monthly, /by-type.
        - Mensagens consistentes: 403 = "Você precisa seguir este usuário
          pra ver as estatísticas dele"; 404 = "Usuário não encontrado".
        - Confirmado com Select-String: 1 definição + 4 chamadas.
        - ruff All checks passed; pytest 129 passed (aditivo).

    test_stats.py:
        - +helpers _make_follow e _client_as (este último monta AsyncClient
          com override local de get_db e get_current_user, reaproveitando
          test_engine session-scoped; NÃO toca no conftest).
        - +7 testes na seção S19.
        - Confirmado com Select-String.
        - ruff All checks passed; pytest 136 passed in 32.68s.

    Commit 229e36b, push aceito. Render redeploya.

    Validação em produção:
        /auth/me → id 01a12c83-be2a-71fa-b966-1c93ca64f341 (prod).
        /users/{prod}/stats/summary → 6 atividades, 26.443,22 m, 18.679 s,
          5.411,6 m elev, 1.091 cal, pace 706,38 s/km, speed 1,42 m/s.
        weekly {weeks: 8, items} com period_start sempre segunda.
        monthly {months: 6, items} com period_start sempre dia 01.
        by-type?period=90d → items [{activity_type: "walk", ..., previous:
          null}] — previous presente (prova do deploy), null porque prod
          não tem walk na janela [now-180d, now-90d). Não é bug.
        (Erro inicial: usei /users/me → 422. Correto é /auth/me. Lição
        registrada.)

3.5 [Front] Implementação

    Ordem de entrega (uma versão por arquivo por resposta, com build):

        api/stats.ts (só adiciona 4 funções; as originais intocadas)
        hooks/useStats.ts (só adiciona keys namespaced e 4 hooks novos)
        pages/ProfilePage.tsx (adiciona canView/showOtherStats, 8 hooks,
          seleção de fonte, e troca {isSelf &&} por {canView &&})

    Build verde em cada um:
        stats.ts: 824 modules, ProfilePage 15.98 kB (sem consumidor novo).
        useStats.ts: 824 modules, ProfilePage 16.23 kB (+0.25 kB — tree-shaking
          não removeu porque o módulo já é importado pelo ProfilePage).
        ProfilePage.tsx: 824 modules, ProfilePage 17.52 kB (+1.29 kB).

    Nenhum erro de TS.

3.6 Validação visual (produção)

    Conta prod@rumo.com (id 01a12c83-...), logado no navegador.
    prod segue Prod2 (id 01a141e7-..., 2 atividades, 14.643,22 m, pace
    496,89 s/km, 0 kcal).

    Cenário 1 — /users/01a12c83-... (self):
        Seção de stats normal: 6 atividades, 26.443 m, pace ~11:46/km.
        Network: 4 requests para /activities/stats/*, nenhuma para
        /users/.../stats/*. OK.

    Cenário 2 — /users/01a141e7-... (Prod2, seguido):
        Seção de stats com 2 atividades, 14.643 m, pace ~8:17/km, 0 kcal.
        Network: 4 requests para /users/01a141e7-.../stats/*, nenhuma para
        /activities/stats/*. OK — dados do alvo, sem vazamento.

    Cenário 3 — terceiro não seguido:
        Sem seção de stats. Network: zero requests no filtro "stats". OK.

    Resultado do usuário: "tudo ok, aparentemente".

3.7 Estado final da sessão

    Working tree limpo, main == origin/main == HEAD == 0df0b9f.
    npm run build: verde (824 modules, ProfilePage 17.52 kB).
    pytest -q: 136 passed, 0 warnings (local).
    ruff check .: All checks passed.
    flutter analyze: No issues found (não tocado na S19).
    Backend em produção: 4 endpoints /users/{id}/stats/* respondendo.
    Front em produção: validado visualmente nos 3 cenários.
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
    "coordinates": [[lon, lat], ...],   // GeoJSON
    "bbox": [minLon, minLat, maxLon, maxLat],
    "n_points": 60,
    "simplified": false
    }

    ActivityResponse (feed/lista/detalhe/busca):
    { ..., "bbox": [minLon, minLat, maxLon, maxLat] | null }
    Ordem GeoJSON. Null quando route IS NULL. Sem N+1.

    GET /activities/stats/summary?activity_type=<opcional>
    → StatsSummary: total_activities, total_distance_m, total_duration_s,
      total_elevation_gain_m, total_calories, avg_pace_s_per_km,
      avg_speed_mps.

    GET /activities/stats/weekly?weeks=N&activity_type=<opcional>
    → StatsWeeklyResponse: { weeks, items: [StatsPeriod] }.
      StatsPeriod: period_start (segunda), total_activities,
      total_distance_m, total_duration_s, total_calories.

    GET /activities/stats/monthly?months=N&activity_type=<opcional>
    → StatsMonthlyResponse: mesmo shape, chave "months", period_start
      "YYYY-MM-01".

    GET /activities/stats/by-type?period=<all|90d|1y> (S17 + S18)
    → StatsByTypeResponse: { items: [StatsByTypeItem] }.
      StatsByTypeItem: activity_type, total_activities, total_distance_m,
      total_duration_s, total_elevation_gain_m, total_calories,
      previous: StatsByTypePreviousItem | null.
      StatsByTypePreviousItem: as 5 métricas (sem activity_type).
      Só tipos com >= 1 atividade na janela ATUAL aparecem.
      Ordenação: total_activities DESC, activity_type ASC (Python).
      period inválido → 422. previous null para period="all" ou tipo
      ausente na janela anterior.

    [Sessão 19] GET /users/{user_id}/stats/summary    (mesmo shape acima)
    [Sessão 19] GET /users/{user_id}/stats/weekly     (mesmo shape; weeks 1-52)
    [Sessão 19] GET /users/{user_id}/stats/monthly    (mesmo shape; months 1-24)
    [Sessão 19] GET /users/{user_id}/stats/by-type    (mesmo shape; period all|90d|1y)
    Permissão (helper _ensure_can_view_stats):
      - self: 200.
      - viewer segue target: 200.
      - viewer não segue: 403 "Você precisa seguir este usuário pra ver as
        estatísticas dele".
      - target inexistente: 404 "Usuário não encontrado".
    Os 4 reaproveitam stats_service.* sem mudança de assinatura.
    by-type mantém previous (mesma semântica da S18).

    Endpoints de stats (todos, /activities e /users) NÃO aceitam user_id
    para "ver de outro" fora da regra de follow. A UI só mostra stats no
    perfil quando canView = isSelf || isFollowing.

    GET /auth/me — identidade do usuário logado (S19: NÃO é /users/me).
    Resposta: { id, email, username, full_name, weight_kg, height_cm,
    birth_date, is_active, created_at }.

===============================================================================

    COMMITS PENDENTES / ESTADO DO REPO
    ===============================================================================

    Sessões 9 a 19 commitadas e pushadas.
    origin/main == main == HEAD == 0df0b9f.
    Sessão 19 fechada com este handoff (a commitar como
    "docs: handoff da Sessao 19" na próxima ação).
    Nenhuma pendência conhecida de git.

===============================================================================

    SCRIPTS ÚTEIS (PowerShell)
    ===============================================================================

[Sessão 20 — primeira ação] Abrir PowerShell via Win+R → "powershell"
(NÃO abrir de dentro do VS Code / Windows Terminal)
Depois:
[Sessão 20 — primeira ação] Estado do repo (sem abrir o less)

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short
[Sessão 20 — primeira ação] Descoberta da estrutura do repo

Get-ChildItem -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app\routers -File | Select-Object Name
Get-ChildItem D:\Rumo\backend\tests -File | Select-Object Name
[Sessão 20 — primeira ação] Sanidade de build

cd D:\Rumo\web
npm run build
cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
[Sessão 20 — primeira ação] Docker + pytest local

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps
# Se o prompt já mostra (venv), PULE a linha abaixo.
.\venv\Scripts\Activate.ps1      # UM ponto, NÃO dois
python -m pytest -q              # esperado: 136 passed
Verificar que fitdecode está instalado e fitparse NÃO

python -c "from importlib.metadata import version; print('fitdecode', version('fitdecode'))"
python -c "import fitparse" 2>&1   # esperado: ModuleNotFoundError
[Sessão 20 — primeira ação] Detecção de versão em produção (S19 — stats de terceiros)

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id
$resp = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/summary" -Headers @{ Authorization = "Bearer $token" }
Write-Host "RESULTADO: S19 no ar (summary do /users/{id}/stats: $($resp.total_activities) atividades)"
Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id
Stats de terceiros (S19)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/monthly?months=6" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
Quem prod segue (para o cenário "terceiro seguido")

$prod2Id = "01a141e7-5ea4-7600-8959-19145475ad0a"
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$prod2Id/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/01a12c83-be2a-71fa-b966-1c93ca64f341/following" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Stats do self (comportamento antigo, para comparar)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=all" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
Ruff (backend)

cd D:\Rumo\backend
# Se o prompt já mostra (venv), pule:
.\venv\Scripts\Activate.ps1
ruff check .
===============================================================================

    DÍVIDAS TÉCNICAS
    ===============================================================================

    (CONHECIDA — Sessão 19) Existem duas pastas de venv em D:\Rumo\backend:
    .venv (antiga, provavelmente Python 3.12 ou 3.11, não usada) e venv
    (Python 3.13.7, ativa). O `Remove-Item -Recurse -Force .\.venv` falhou
    na S19 com "acesso negado a ruff.exe" (processo do VS Code segurando o
    binário). Higiene pendente: com VS Code fechado, rodar
        Get-Process ruff -ErrorAction SilentlyContinue | Stop-Process -Force
        cd D:\Rumo\backend
        Remove-Item -Recurse -Force .\.venv
    Não bloqueia nada, mas confunde o Pylance (ver lição S19 de
    "interpretador errado").

    (CONHECIDA — S19) Pylance pode reclamar de imports (fastapi, sqlalchemy,
    pytest, httpx) porque o VS Code aponta para o interpretador errado.
    Terminal está certo. Correção documentada na seção 0 (Select Interpreter
    → D:\Rumo\backend\venv\Scripts\python.exe). Se persistir, criar
    .vscode/settings.json com python.defaultInterpreterPath.

    (ARMADILHA CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela
    ORDEM DE DECLARAÇÃO, não pela string. get_by_type faz o desempate final
    em Python: items.sort(key=lambda r: (-r["total_activities"],
    r["activity_type"])). REGRA: qualquer novo ORDER BY em coluna Enum DEVE
    (a) fazer o sort final em Python, ou (b) ser testado contra a ordem de
    declaração.

    (CONHECIDA — Sessão 17) Filtro `period` usa `now()` do Postgres. Testes
    de `period` DEVEM usar `datetime.now(timezone.utc) - timedelta(days=N)`
    com margem >= 10 dias entre dentro e fora da janela. Não misturar com
    `_dt` fixo.

    (CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN.
    Quando um SELECT precisa somar duas janelas, o WHERE deve cobrir a união
    (ex.: started_at >= now - 2N) e cada métrica recorta sua janela via
    SUM(CASE WHEN <janela> THEN col ELSE 0 END) — inclusive a contagem.
    Depois, filtrar em Python as linhas cuja janela principal ficou zerada.

    (CONHECIDA — Sessão 17/18, reafirmada na S19) StatsCards mostra summary
    "todos os tempos", não filtrado por period nem por previous. O segmented
    control de período afeta APENAS a tabela por tipo. Intencional.

    (CONHECIDA — Sessão 17/18/19) Conta prod@rumo.com não tem atividade
    >90d (na janela anterior). Por isso period=all, 90d e 1y retornam iguais
    em produção para prod, e previous vem null em todos os itens. Para ver
    diferença em produção, usar Prod2 ou upload de GPX com data no passado.
    NÃO PERDER TEMPO achando que está quebrado — os 136 testes locais
    (com _dt_ago(120), _dt_ago(500)) provam o filtro e o previous.

    (Oportunidade — S18/S19) Delta "vs. anterior" cobre 3 métricas
    (atividades, distância, elevação). Tempo e calorias ficaram fora por
    legibilidade. Extensão trivial se virar requisito (mais 2 DeltaLine).

    (Oportunidade — S18/S19) Semântica do delta é NEUTRA (subiu=verde,
    desceu=vermelho, igual=cinza). Sem juízo de "melhor/pior". Se o produto
    quiser meta, é feature nova.

    (Oportunidade — S19) Stats públicas hoje só aparecem quando viewer segue
    o alvo. Se o produto quiser "stats públicas sempre" (ex.: perfil aberto),
    é mudança de regra no _ensure_can_view_stats (endpoint + teste + front).
    Não é bug — é decisão de privacidade documentada.

    (Oportunidade) RouteMap.tsx é reutilizável. Se aparecer segundo uso,
    considerar React.lazy() para tirar o leaflet (163.60 kB) do chunk.

    (Oportunidade) Drill-down por tipo poderia ganhar:
        - Comparação year-over-year (Opção 1 do handoff da S18).
        - Filtro de período custom (ex.: "últimos 180 dias"). Hoje é
          all|90d|1y fixo; adicionar valor ao Literal é aditivo.
        - Export CSV/GPX (Opção 3).

    Mobile: sem drill-down de stats no app. Sem inclinação/rotação 3D.
    TimeoutException do app mobile não reproduzido desde a Sessão 9.

===============================================================================

    PRÓXIMOS PASSOS RECOMENDADOS (Sessão 20 e além)
    ===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 20 (antes de qualquer mudança de código):

    No terminal (PowerShell via Win+R → "powershell"):
    cd D:\Rumo
    git push
    git --no-pager log --oneline -8
    git status --short
    cd web ; npm run build
    cd ..\mobile
    & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
    Confirmar: push aceito, HEAD == origin/main == 0df0b9f (ou o commit do
    handoff, se for o caso), build e analyze verdes, working tree limpo.

    DOCKER + PYTEST LOCAL:
    docker version
    docker compose version
    cd D:\Rumo\backend
    docker compose -f docker-compose.test.yml up -d
    docker ps
    # Se prompt já mostra (venv), pular:
    .\venv\Scripts\Activate.ps1     # UM ponto
    python -m pytest -q
    Esperado: 136 passed, 0 warnings.

    DETECÇÃO DE VERSÃO EM PRODUÇÃO (S19 — stats de terceiros):
    Rodar o script da seção 6 ("Detecção de versão em produção (S19 —
    stats de terceiros)"). Esperado: "S19 no ar (summary do
    /users/{id}/stats: 6 atividades)". Se der 404, o Render não redeployou
    — checar dashboard do Render.

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

    HIGIENE OPCIONAL (recomendada): remover .venv antiga com VS Code
    fechado (ver Dívidas Técnicas).

ESTADO DA ROTA B (Sessão 19): TRÊS ITENS FECHADOS.
Filtro de período (S17) + comparação com janela anterior (S18) + stats
públicas em perfis de terceiros (S19) → FEITOS e em produção (0df0b9f).

A ROTA B SEGUE ABERTA para os demais itens. Próximos passos exigem
ESCOLHA entre:

OPÇÃO 1 — Comparação "este período vs. MESMO período do ano anterior"
    (year-over-year).
    Backend: nova semântica, provavelmente param adicional (compare=prev|yoy)
    ou endpoint novo. MEXE EM CONTRATO — decidir antes de codar.
    Front: reaproveita PreviousDelta, rótulo "vs. ano anterior".
    ATENÇÃO: prod não tem dado >90d, então year-over-year com 90d não mostra
    diferença em produção. Testável só local (ou com Prod2).

OPÇÃO 2 — Export de atividades (CSV/GPX).
    Escopo maior. Desenhar contrato + schema + teste + UI.
    GPX já existe no backend (gpx_service.py) — provavelmente reutilizável.
    CSV é mais simples (Excel/Sheets).

OPÇÃO 3 — Stats no app mobile (drill-down por tipo no Flutter).
    Mobile está parado desde S11. Se for evoluir, é sessão grande.
    Decidir se vale antes de começar.

OPÇÃO 4 — Resíduos de baixo risco da Rota A+ (b)/(c) + higiene.
    (b) RouteMap com React.lazy() — prepara terreno para segundo uso.
    (c) Cheat sheet de endpoints num README.
    (d) Remover .venv antiga (higiene, dívida da S19).
    Ganho marginal. Recomendação: só se não houver Rota B clara.

RECOMENDAÇÃO PARA A SESSÃO 20:

Antes de escolher, VALIDAR ESTADO (seção 6 — primeira ação). Se estiver
tudo verde (build, analyze, pytest 136, endpoints /users/{id}/stats/* no ar),
aí escolher.

Minha recomendação de rota: OPÇÃO 4 (higiene) **primeiro**, como
aquecimento de 30–60 min, seguida de OPÇÃO 1 (year-over-year) ou OPÇÃO 2
(export). Motivos:
  - A higiene da .venv é trivial e elimina a confusão do Pylance de vez.
  - A S19 entregou uma feature visível e arriscada (privacidade); a S20
    pode começar com algo de baixo risco para "esquentar" e reduzir a
    chance de regressão.
  - Entre year-over-year e export, year-over-year reaproveita 100% da
    infra das S17/S18 (previous, delta, PreviousDelta no front) e é
    testável 100% local — menor risco. Export é maior e mexe em contrato
    novo (CSV schema, UI de download).

  Se o usuário preferir escopo maior e visível, OPÇÃO 2 (export GPX/CSV).
  Se preferir mobile, OPÇÃO 3 — mas é sessão grande, avisar antes.

Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes do
fim, parar e entregar o HANDOFF completo da Sessão 20 neste mesmo formato
(seções 0 a 8).