HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 18

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
    (129 passed ao fim da Sessão 18). Container de teste rumo_postgres_test
    na porta 5433. Para reativar numa sessão nova: (1) abrir Docker Desktop e
    esperar a baleia verde; (2) garantir que o terminal foi aberto via Win+R
    (fora do VS Code / Windows Terminal, que herdam PATH antigo);
    (3) cd D:\Rumo\backend; (4) docker compose -f docker-compose.test.yml up -d;
    (5) ..venv\Scripts\Activate.ps1 (pular se o prompt já mostra (.venv));
    (6) pytest -q.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada na Sessão 17 e mantida na S18:

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
        └── types\ # api.ts (todos os tipos, StatsByTypePrevious — S18)

DIVERGÊNCIAS vs handoff da Sessão 17:

    backend/app/services/stats_service.py: get_by_type ganhou comparação
    com a janela anterior. Novo helper _current_window_expr; WHERE ampliado
    para 2N dias quando period != "all"; métricas atuais via CASE WHEN;
    previous montado em Python. get_summary e get_period_stats intocados.

    backend/app/schemas/stats.py: +StatsByTypePreviousItem; +campo
    previous: StatsByTypePreviousItem | None = None em StatsByTypeItem.

    backend/tests/test_stats.py: +5 testes de previous (service + rota).
    Total: 129 passed (era 124 na S17).

    web/src/api/stats.ts: SÓ DOCSTRING de getStatsByType ganhou parágrafo
    S18. Sem mudança de código.

    web/src/hooks/useStats.ts: SÓ 3 comentários S18. Sem mudança de código.

    web/src/types/api.ts: +StatsByTypePrevious; +campo
    previous: StatsByTypePrevious | null em StatsByTypeItem (obrigatório
    no tipo, não opcional — o backend sempre envia null quando não aplica).

    web/src/pages/ProfilePage.tsx: +showPrevious; +<th> e <td> "vs. anterior"
    condicionais; +componentes PreviousDelta e DeltaLine (no fim do arquivo).
    Todo o resto intocado (filtros, toggles, StatsCards, PeriodChart, lista).

    backend/app/routers/activities.py: INTOCADO na S18 (period já existia
    desde a S17; previous é derivado no service, declarado no schema,
    serializado pelo FastAPI).

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

        pytest -q — esperado: 129 passed, 0 warnings (verde na Sessão 18)

    Se Activate.ps1 der erro de política:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

COMO TESTAR O BACKEND DE PRODUÇÃO SEM O APP (PowerShell)

    Login (retorna JWT):
    $body = "username=prod@rumo.com&password=senha12345"
    $login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
    $token = $login.access_token

    Stats by-type COM previous (S18 — validado em produção):
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=all"  -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=90d"  -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
    Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=1y"   -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

    Conta de teste: prod@rumo.com / senha12345.
    NOTA — essa conta tem 3 walk (todas <90d). Por isso period=all, period=90d
    e period=1y retornam IGUAIS, e "previous" vem null em TODOS os itens
    (não há atividade na janela anterior). NÃO é bug — é ausência de dado
    antigo. Os 129 testes locais (com _dt_ago(120), _dt_ago(500)) provam
    o filtro e o previous de verdade. NÃO PERDER TEMPO achando que está
    quebrado.

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

    ATENÇÃO (S17) — arquivo "salvo" que não salvou. A S17 perdeu dois rounds
    porque o Ctrl+S não foi feito (ou foi feito em outro buffer/arquivo).
    SINTOMA: build ou pytest falha dizendo que um símbolo novo não existe,
    mesmo o assistente tendo entregado o arquivo. DIAGNÓSTICO RÁPIDO:
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

    ATENÇÃO (S18 — NOVO) — "422 de versão" NÃO distingue S17 de S18.
    O endpoint /activities/stats/by-type?period=30d devolve 422 desde a S17
    (period já existia). Para saber se o Render redeployou a S18, o check
    correto é: GET ?period=90d e verificar se o item tem a CHAVE "previous"
    (valor null é OK). Se a chave não existir, o Render ainda está na S17.
    NÃO confundir "backend de pé" com "S18 no ar".

    ATENÇÃO (S18 — NOVO) — WHERE mata a janela anterior antes do CASE WHEN.
    Regra aprendida: quando um único SELECT precisa somar duas janelas de
    tempo, o WHERE NÃO pode filtrar só a janela atual — ele descarta as
    linhas da janela anterior ANTES do CASE WHEN chegar nelas. Solução:
    ampliar o WHERE para cobrir as duas janelas (started_at >= now - 2N) e
    fazer o recorte da janela atual DENTRO de cada métrica, via
    SUM(CASE WHEN <janela_atual> THEN col ELSE 0 END), inclusive a contagem
    (SUM(CASE WHEN ... THEN 1 ELSE 0 END)). Detalhe na seção 7.

ACORDOS DE TRABALHO (válidos em todas as sessões)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão
    pendente, executar a recomendada salvo instrução explícita em contrário.
    (Usuário reforçou isso no início das Sessões 15, 16, 17 e de novo na 18:
    "sempre vamos fazer o que você recomenda".)

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff
    parcial, nunca "// resto igual". Preservar imports, comentários e trechos
    que já funcionam. Destacar o trecho alterado com comentário curto acima
    (// [Sessão N] ou // [Sessão N — fix]).

    UMA versão por arquivo por resposta. Se errar no meio do raciocínio,
    cortar a versão errada e entregar só a corrigida com nota de 1 linha.
    NUNCA duas versões do mesmo arquivo na mesma resposta. (A S18 violou
    essa regra uma vez com o ProfilePage.tsx — entregou uma versão com bug
    no PreviousDelta e, na mesma resposta, a corrigida. O usuário não
    reclamou, mas foi erro do assistente. NÃO repetir: se errar, cortar a
    versão errada e entregar só a corrigida.)

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

    Backend: 129 testes passando LOCALMENTE (pytest -q verde na Sessão 18),
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
            (S18) Cada item ganhou "previous" (janela imediatamente anterior)
            ou null (quando period="all" ou tipo ausente na janela anterior).

    Os 3 primeiros endpoints de stats (summary/weekly/monthly) aceitam
    activity_type opcional. O by-type NÃO aceita activity_type (é o
    drill-down por tipo — filtrar por tipo derrotaria o propósito).

    Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet
    (RouteMap no detalhe) + recharts (gráficos no perfil). Drill-down por
    tipo tem segmented control de janela temporal (S17) e, quando period
    != "all", coluna "vs. anterior" com delta (Ativ./Dist./Elev.) colorido
    (S18).

    Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
    alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds.
    Sem drill-down de stats no app.

    [Sessão 18 — entregas]

        Backend — comparação com janela imediatamente anterior.

            schemas/stats.py: +StatsByTypePreviousItem (5 métricas, sem
            activity_type). StatsByTypeItem ganhou
            previous: StatsByTypePreviousItem | None = None.

            services/stats_service.py: get_by_type estendido. Novo
            _current_window_expr (condição started_at >= now - N).
            _previous_window_expr (já existia da entrega interna, mas é
            o helper que define [now-2N, now-N)). WHERE ampliado para
            started_at >= now - 2N quando period != "all". Métricas da
            janela atual via SUM(CASE WHEN <janela_atual> THEN col ELSE 0
            END), inclusive contagem. Métricas da janela anterior via
            SUM(CASE WHEN <janela_anterior> THEN col ELSE 0 END). previous
            montado em Python; null quando prev_total_activities == 0.
            Loop pula linhas com curr_activities == 0 (tipo só na janela
            anterior não aparece). get_summary e get_period_stats INTOCADOS.

            tests/test_stats.py: +5 testes:
              - test_get_by_type_previous_90d (45d atual, 120d anterior)
              - test_get_by_type_previous_1y (200d atual, 500d anterior)
              - test_get_by_type_previous_all_is_none (period=all → null)
              - test_get_by_type_previous_none_when_type_absent_in_window
                (item existe, previous null)
              - test_route_by_type_previous_shape (shape HTTP com as 5
                chaves exatas em 90d; null em all)
            Total: 129 passed.

        Web — coluna "vs. anterior" no drill-down por tipo.

            types/api.ts: +StatsByTypePrevious (5 campos). StatsByTypeItem
            ganhou previous: StatsByTypePrevious | null (obrigatório no tipo;
            null é valor válido, não undefined).

            pages/ProfilePage.tsx: +import type { StatsByTypeItem };
            +const showPrevious = byTypePeriod !== "all"; +<th> "vs. anterior"
            condicional; +<td> com <PreviousDelta item={item} /> condicional;
            +componentes PreviousDelta e DeltaLine no fim do arquivo.
            PreviousDelta mostra 3 linhas: Ativ./Dist./Elev., com delta
            absoluto e percentual (percentual só quando previous > 0), cor
            verde (subiu) / vermelho (desceu) / cinza (igual). null → "—".
            DeltaLine recebe current, previous, formatter opcional.

            api/stats.ts: SÓ DOCSTRING de getStatsByType ganhou parágrafo S18.
            hooks/useStats.ts: SÓ 3 comentários S18.

        Estado final: working tree limpo, HEAD == origin/main == b0e3a29,
        pytest 129 passed / 0 warnings (local), ruff All checks passed,
        npm run build verde (824 modules, ProfilePage 15.98 kB), flutter
        analyze sem issues, Render deployado (previous presente na
        resposta do period=90d em produção), Vercel redeployado (timing
        pós-push, não validado visualmente — próxima sessão pode conferir
        abrindo https://rumo-wheat.vercel.app e indo em /users/me ou
        equivalente).

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

    Git (estado ao fim da Sessão 18):
    b0e3a29 (HEAD -> main, origin/main) feat(stats): comparacao com janela anterior no drill-down por tipo (Sessao 18)
    494d8cc docs: handoff da Sessao 17
    5925a03 feat(stats): filtro de periodo no drill-down por tipo (90d|1y|all)
    0f1c6ef chore(web): remove bboxToOsmTileUrl deprecated da Sessao 16
    1ab793d docs: handoff da Sessão 16
    a8a515f feat(web): miniatura do feed em mosaico 2x2 de tiles OSM
    05185f0 docs: handoff da Sessão 15
    4cfd099 refactor(web): StatsCards usa formatElevation em vez de inline
    fdac345 feat(web): coluna de elevacao no drill-down por tipo
    3cf7668 refactor(backend): migra parsing de .FIT de fitparse para fitdecode

    Todos os commits estão em origin/main (pushados).

    Render e Vercel deployam automático a cada push em main. A Sessão 18
    está deployada em produção (validado via "previous": null no
    period=90d).

===============================================================================

    O QUE FOI FEITO NA SESSÃO 18
    ===============================================================================

3.1 Validação de estado inicial (Sessão 18)

    PowerShell via Win+R, repo em D:\Rumo, venv backend ativo.

    git push: Everything up-to-date.

    HEAD == origin/main == 5925a03 (commit da S17, antes do handoff).

    git status --short: docs/HANDOFF.md modificado (handoff da S17 ainda
    não commitado).

    npm run build: 824 modules, verde.

    flutter analyze: No issues found.

    docker ps: rumo_postgres_test healthy.

    pytest -q: 124 passed (estado da S17).

    Detecção de versão em produção: 422 em period=30d. S17 deployada.

    Commit do handoff da S17: 494d8cc (docs: handoff da Sessao 17).

3.2 Definição de contrato (antes de codar)

    Usuário reforçou "sempre vamos seguir suas recomendações".

    Contrato fixado:

        - "Anterior" = janela imediatamente anterior, sem sobreposição:
          90d → [now-180d, now-90d); 1y → [now-730d, now-365d).
        - period="all" → sem comparação (previous is None).
        - previous aninhado no item; null quando period="all" ou quando
          o tipo não tem atividade na janela anterior.
        - Implementação (A): um único SELECT, SUM(CASE WHEN ...) por
          métrica; sem N+1.
        - Front: coluna "vs. anterior" no ProfilePage, visível só em
          period != "all"; delta absoluto + percentual; verde/vermelho/cinza.
        - Fora de escopo: StatsCards (summary "todos os tempos"), mobile,
          get_summary, get_period_stats.

3.3 [Backend] Implementação + testes

    Ordem de entrega (uma versão por arquivo por resposta):

        stats_service.py (completo)
        schemas/stats.py (completo)
        tests/test_stats.py (completo)

    Cada um: usuário cola Get-Content -Encoding UTF8, assistente entrega
    arquivo completo, usuário confirma com Select-String (padrão S17),
    depois pytest -q.

    Rounds:

        stats_service.py: 124 passed (o campo previous não estava no
        schema ainda, então testes antigos intocados).

        schemas/stats.py: 124 passed.

        tests/test_stats.py: 3 FAILED, 126 passed.
        Falhas: test_get_by_type_previous_90d, test_get_by_type_previous_1y,
        test_route_by_type_previous_shape — todos com
        "assert prev is not None" falhando.

    Diagnóstico (S18 — lição principal):

        O get_by_type usava WHERE started_at >= now - N (só janela atual)
        e CASE WHEN <janela_anterior> para previous. O WHERE descartava
        as linhas da janela anterior ANTES do CASE WHEN — previous vinha
        sempre null. Os 3 testes capturaram o bug corretamente.

    Fix (entregue em stats_service.py completo, uma versão só):

        - Novo helper _current_window_expr(period).
        - Quando period != "all": WHERE vira started_at >= now - 2*N.
        - Métricas atuais (5 originais) viram SUM(CASE WHEN <janela_atual>
          THEN col ELSE 0 END), inclusive count
          (SUM(CASE WHEN ... THEN 1 ELSE 0 END)).
        - Loop pós-SQL pula linhas com curr_activities == 0.
        - previous montado em Python; null quando prev_total_activities == 0.

    Após o fix: 129 passed em 34.83s.

3.4 [Front] Implementação

    Ordem de entrega (uma versão por arquivo por resposta, com build):

        api/stats.ts (só docstring — tipos moram em types/api.ts)
        types/api.ts (tipo novo StatsByTypePrevious + campo previous)
        hooks/useStats.ts (só comentários — sem mudança de código)
        pages/ProfilePage.tsx (coluna vs. anterior)

    Build verde em cada um. ProfilePage cresceu 14.95 kB → 15.98 kB
    (+1.03 kB, dentro do esperado).

    ERRO DO ASSISTENTE (registrado como lição):

        O ProfilePage foi entregue DUAS VEZES na mesma resposta — a primeira
        versão tinha um bug de design no PreviousDelta (recebia só
        `previous`, não o item inteiro, e não conseguia computar delta/cor).
        O assistente tentou remendar com comentário "NOTA DE IMPLEMENTAÇÃO"
        e entregou a versão corrigida logo abaixo. Isso violou a regra
        "UMA versão por arquivo por resposta". O usuário não salvou a
        errada (avisado com "⚠️ Pare — antes de salvar, preciso corrigir"),
        então não houve retrabalho, mas foi erro de processo.
        PRÓXIMAS SESSÕES: se errar no meio da escrita, cortar a versão
        errada e entregar SÓ a corrigida.

3.5 Estado final da sessão

    Working tree limpo, main == origin/main == b0e3a29.

    npm run build: verde (824 modules).

    pytest -q: 129 passed, 0 warnings (local).

    ruff check .: All checks passed.

    flutter analyze: No issues found (não tocado na S18).

    Backend em produção: "previous": null presente no period=90d
    (Sessão 18 deployada no Render).

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

    GET /activities/stats/by-type?period=<all|90d|1y> (S17 + S18)
    → StatsByTypeResponse:
    {
    "items": [
    {
    "activity_type": "run", // string
    "total_activities": 12,
    "total_distance_m": 84000.0,
    "total_duration_s": 25200,
    "total_elevation_gain_m": 1200.0,
    "total_calories": 4200,
    // S18: janela imediatamente anterior, ou null.
    "previous": {
    "total_activities": 9,
    "total_distance_m": 61000.0,
    "total_duration_s": 18300,
    "total_elevation_gain_m": 900.0,
    "total_calories": 3100
    } // ou null
    },
    ...
    ]
    }
    Só tipos com >= 1 atividade NA JANELA ATUAL aparecem.
    Ordenação garantida: total_activities DESC, activity_type ASC (Python).
    period: "all" (default) | "90d" | "1y". Valores inválidos → 422.
    Janela atual: started_at >= now - N. Janela anterior:
    started_at >= now - 2N e started_at < now - N.
    previous: null se period="all" ou se não há atividade do tipo na
    janela anterior (todas as 5 métricas zero).

    Todos os endpoints de stats são do current_user (não aceitam user_id).
    A UI só mostra stats no próprio perfil (isSelf).

===============================================================================

    COMMITS PENDENTES / ESTADO DO REPO
    ===============================================================================

    Sessões 9 a 18 commitadas e pushadas.

    origin/main == main == HEAD == b0e3a29.

    Sessão 18 fechada com este handoff (a commitar como
    "docs: handoff da Sessao 18" na próxima ação).

    Nenhuma pendência conhecida de git.

===============================================================================

    SCRIPTS ÚTEIS (PowerShell)
    ===============================================================================

[Sessão 19 — primeira ação] Abrir PowerShell via Win+R → "powershell"
(NÃO abrir de dentro do VS Code / Windows Terminal)
Depois:
[Sessão 19 — primeira ação] Estado do repo (sem abrir o less)

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short
[Sessão 19 — primeira ação] Descoberta da estrutura do repo

Get-ChildItem -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app\routers -File | Select-Object Name
Get-ChildItem D:\Rumo\backend\tests -File | Select-Object Name
[Sessão 19 — primeira ação] Sanidade de build

cd D:\Rumo\web
npm run build

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
[Sessão 19 — primeira ação] Docker + pytest local

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
[Sessão 19 — primeira ação] Detecção de versão em produção (S18 — campo previous)

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$resp = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=90d" -Headers @{ Authorization = "Bearer $token" }
$first = $resp.items | Select-Object -First 1
if ($first.PSObject.Properties.Name -contains "previous") {
    Write-Host "RESULTADO: S18 no ar (campo previous presente; valor = $($first.previous))"
} else {
    Write-Host "RESULTADO: backend AINDA na S17 (sem campo previous)"
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
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type?period=all" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4
Track (produção)

$t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/<id>/track" -Headers @{ Authorization = "Bearer $token" }
Ruff (backend)

cd D:\Rumo\backend
..venv\Scripts\Activate.ps1
ruff check .

===============================================================================

    DÍVIDAS TÉCNICAS
    ===============================================================================

    (ARMADILHA CONHECIDA — decisão da Sessão 14, documentada na S15/S16/S17)
    Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO, não pela
    string. Activity.activity_type é Enum nativo (run, walk, cycle, hike,
    swim, other). ORDER BY activity_type no SQL devolve nessa ordem.
    DECISÃO: get_by_type (stats_service.py) faz o desempate final em Python:
    items.sort(key=lambda r: (-r["total_activities"], r["activity_type"]))
    REGRA PARA O FUTURO: qualquer novo ORDER BY em coluna Enum DEVE (a) fazer
    o sort final em Python, ou (b) ser explicitamente testado contra a ordem
    de declaração do enum. Não confiar em ORDER BY direto em coluna Enum.

    (CONHECIDA — Sessão 17) Filtro `period` usa `now()` do Postgres.
    A janela retroativa é calculada com `func.now() - timedelta(...)` — ou
    seja, o relógio de referência é o do servidor de banco, não o do
    processo Python. Testes determinísticos com `_dt(2026, 1, 5)` NÃO servem
    para testar `period` — precisam usar datas relativas a `now()`. Foi por
    isso que a S17 adicionou `_dt_ago(days)` no test_stats.py. REGRA:
    qualquer teste de `period` (ou de outra feature baseada em `now()`) DEVE
    usar `datetime.now(timezone.utc) - timedelta(days=N)` com margem ≥ 10
    dias entre dentro e fora da janela. Não misturar com `_dt` fixo.

    (NOVA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN.
    Quando um único SELECT precisa somar duas janelas de tempo, o WHERE do
    SELECT não pode filtrar só a janela atual — ele descarta as linhas da
    janela anterior ANTES de o CASE WHEN chegar nelas, e `previous` vem
    sempre null. O bug foi pego por 3 testes (previous_90d, previous_1y,
    previous_shape) e corrigido na S18.
    REGRA PARA O FUTURO: sempre que uma query precisar de métricas de
    múltiplas janelas no mesmo SELECT, o WHERE deve cobrir a união das
    janelas (ex.: started_at >= now - 2N) e cada métrica recorta sua
    própria janela via SUM(CASE WHEN <janela> THEN col ELSE 0 END) —
    inclusive a contagem, que vira SUM(CASE WHEN ... THEN 1 ELSE 0 END).
    Depois, filtrar em Python as linhas cuja janela "principal" ficou zerada
    (para não mostrar tipos que só existem na janela secundária).

    (CONHECIDA — Sessão 17, reafirmada na S18) StatsCards.tsx mostra
    summary "todos os tempos", não filtrado por `period` nem por
    `previous`. O segmented control de período afeta APENAS a tabela por
    tipo. Isso é intencional — summary é "totais gerais" e fica no topo
    da página; a tabela é drill-down. Se um dia o usuário quiser filtro
    no summary, é feature nova.

    (CONHECIDA — Sessão 17, reafirmada na S18) Conta prod@rumo.com sem
    atividades com mais de 90 dias. Por isso period=all, period=90d e
    period=1y retornam IGUAIS em produção, e previous vem null em todos
    os itens. Para testar o filtro e o previous em produção com diferença
    visível, seria preciso (a) upload de GPX com data no passado, ou
    (b) aceitar os 129 testes locais como prova (recomendado — são mais
    fortes que qualquer teste de produção nessa conta). NÃO PERDER TEMPO
    achando que está quebrado.

    (Oportunidade) RouteMap.tsx é reutilizável em qualquer página que
    renderize uma rota. Hoje só é usado em ActivityDetailPage. Se aparecer
    um segundo uso, considerar React.lazy() para tirar o leaflet (163.60 kB)
    do chunk da página que não mostra mapa. Ganho hoje é marginal.

    (Oportunidade — S18) Delta "vs. anterior" hoje cobre 3 métricas
    (atividades, distância, elevação). Tempo e calorias ficaram fora por
    legibilidade (3 linhas curtas por célula). Se virar requisito, é
    extensão trivial: adicionar mais 2 DeltaLine no PreviousDelta. Não é
    bug nem dívida — é decisão de UI documentada.

    (Oportunidade — S18) Semântica do delta é NEUTRA: subiu=verde,
    desceu=vermelho, igual=cinza. Não há juízo de "melhor/pior" (ex.:
    pace menor é melhor, mas pace não entra no delta). Se o produto quiser
    semântica de meta ("atingiu objetivo"), é feature nova.

    (Oportunidade) Drill-down de stats por tipo poderia ganhar:
        - Comparação "este período vs. MESMO período do ano anterior" (a
          S18 entregou "janela imediatamente anterior"; a alternativa
          year-over-year é outra feature, com outro contrato).
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

    PRÓXIMOS PASSOS RECOMENDADOS (Sessão 19 e além)
    ===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 19 (antes de qualquer mudança de código):

    No terminal (PowerShell via Win+R → "powershell"):
    cd D:\Rumo
    git push
    git --no-pager log --oneline -8
    git status --short
    cd web ; npm run build
    cd ..\mobile
    & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
    Confirmar: push aceito, HEAD == origin/main == b0e3a29 (ou o commit do
    handoff, se for o caso), build e analyze verdes, working tree limpo.

    DOCKER + PYTEST LOCAL:
    docker version
    docker compose version
    cd D:\Rumo\backend
    docker compose -f docker-compose.test.yml up -d
    docker ps
    # Se prompt já mostra (.venv), pular:
    ..venv\Scripts\Activate.ps1
    pytest -q
    Esperado: 129 passed, 0 warnings.

    DETECÇÃO DE VERSÃO EM PRODUÇÃO (S18 — campo previous):
    Rodar o script da seção 6 ("Detecção de versão em produção (S18 —
    campo previous)"). Esperado: "S18 no ar (campo previous presente;
    valor = )". Se aparecer "backend AINDA na S17", o Render não
    redeployou — checar dashboard do Render.

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

ESTADO DA ROTA B (Sessão 18): PRIMEIRO E SEGUNDO ITENS FECHADOS.
Filtro de período (S17) + comparação com janela anterior (S18) → FEITOS
e em produção (b0e3a29). Backend: /stats/by-type?period=all|90d|1y com
previous opcional. Web: segmented control (S17) + coluna "vs. anterior"
(S18). StatsCards e mobile intocados.

A ROTA B SEGUE ABERTA para os demais itens. Próximos passos exigem
ESCOLHA entre:

OPÇÃO 1 — Comparação "este período vs. MESMO período do ano anterior".
    Backend: nova semântica (year-over-year), provavelmente um param
    adicional (ex.: compare=prev|yoy) ou um endpoint novo.
    MEXE EM CONTRATO — decidir antes de codar.
    Front: reaproveita PreviousDelta, mas com rótulo "vs. ano anterior".
    ATENÇÃO: a conta de teste não tem dado >90d, então year-over-year
    com 90d não vai mostrar diferença em produção. Testável só local.

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

RECOMENDAÇÃO PARA A SESSÃO 19:

Antes de escolher, VALIDAR ESTADO (seção 6 — primeira ação). Se estiver
tudo verde (build, analyze, pytest 129, previous presente em produção),
aí escolher.

Se a escolha for Rota B, minha recomendação é OPÇÃO 2 (stats públicas
em perfis de terceiros) pelos motivos:

  - É evolução natural do produto: o app já mostra perfil de terceiros
    (atividades, seguidores, seguindo), mas esconde stats.
  - Não é mudança de contrato em endpoint existente — é adição de
    endpoints novos. Menos risco de regressão.
  - Valida 100% localmente com pytest (endpoint + service + permissão).
  - Front: 1 condicional no ProfilePage (mostrar StatsCards/PeriodChart/
    by-type para não-self, respeitando follow).
  - Privacidade: só mostra stats se o viewer segue o alvo (mesma regra
    de /activities/{id}/track e do feed).

  ATENÇÃO: a S18 entregou "comparação com janela anterior" recente, e
  a Opção 2 é uma feature visível, mas de escopo maior que a S18 (envolve
  permissão e privacidade). Se o usuário preferir escopo menor, a Opção 1
  (year-over-year) reaproveita toda a infra da S18, mas tem a limitação
  da conta de teste.

Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes
do fim, parar e entregar o HANDOFF completo da Sessão 19 neste mesmo
formato (seções 0 a 8).