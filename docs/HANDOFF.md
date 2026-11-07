===============================================================================
HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 14
===============================================================================

<!-- [Sessão 15] Este arquivo é o handoff da Sessão 14, sendo atualizado ao
longo da Sessão 15. Os acréscimos da Sessão 15 estão marcados com
<!-- [Sessão 15] --> no fonte. Quando a Sessão 15 fechar, o handoff final
(substituindo este arquivo por inteiro) será commitado como
`docs: handoff da Sessão 15`. Até lá, este arquivo serve como referência
viva do estado do projeto. -->

===============================================================================
0. LEIA PRIMEIRO — CONTEXTO OPERACIONAL (evita retrabalho no próximo chat)
===============================================================================

⚠️ REGRA DE OURO PARA O ASSISTENTE NOVO (leia antes de qualquer coisa)
-----------------------------------------------------------------------
VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir
arquivo", "ver o repo". Toda informação sobre o projeto chega por DUAS vias:
  (a) o usuário cola o conteúdo de um arquivo com `Get-Content -Encoding UTF8`
  (b) o usuário cola a saída de um comando de terminal
NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA
reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um
arquivo, PEÇA e espere o usuário colar. Se a estrutura de pastas for
necessária, PEÇA a saída de `Get-ChildItem` (há script pronto na seção 6).
Sessões anteriores perderam tempo porque o assistente tentou "adivinhar" a
árvore de diretórios e errou. Não repetir.

O QUE É LOCAL vs O QUE É PRODUÇÃO
----------------------------------
- LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI
  + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 +
  TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter).
  O assistente NÃO tem acesso a esses arquivos neste chat — o usuário precisa
  colar conteúdo de arquivos e saídas de terminal.
- PRODUÇÃO (na nuvem, acessível por HTTP): backend no Render
  (https://rumo-api-5s0b.onrender.com), frontend web na Vercel
  (https://rumo-wheat.vercel.app). O backend de produção usa Postgres/PostGIS
  gerenciado. Testar via HTTP é sempre possível.
- DOCKER: INSTALADO E FUNCIONAL no Windows local. `pytest -q` local verde
  (118 passed ao fim da Sessão 14). Container de teste `rumo_postgres_test`
  na porta 5433. Para reativar numa sessão nova: (1) abrir Docker Desktop e
  esperar a baleia verde; (2) garantir que o terminal foi aberto via Win+R
  (fora do VS Code / Windows Terminal, que herdam PATH antigo); (3) `docker
  compose -f docker-compose.test.yml up -d`; (4) `pytest -q`.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)
--------------------------------------------------------------------
Árvore de alto nível REAL, confirmada no início da Sessão 14:

D:\Rumo\
├── .vscode\
├── backend\
│   ├── .pytest_cache\
│   ├── .ruff_cache\
│   ├── .venv\          # virtualenv Python ativo (.\.venv\Scripts\Activate.ps1)
│   ├── alembic\
│   ├── app\
│   │   ├── core\
│   │   ├── models\
│   │   ├── routers\    # activities.py, auth.py, comments.py, feed.py,
│   │   │               # notifications.py, photos.py, users.py, __init__.py
│   │   ├── schemas\
│   │   ├── services\   # stats_service.py (get_summary, get_period_stats,
│   │   │               #                 get_by_type — NOVO S14)
│   │   └── __pycache__\
│   ├── samples\
│   ├── scripts\
│   ├── tests\          # conftest.py + test_calories.py + test_comment.py +
│   │                   # test_follow.py + test_like.py + test_stats.py
│   ├── _scratch\
│   └── docker-compose.test.yml
├── docs\
│   └── HANDOFF.md      # este arquivo
├── mobile\
│   └── lib\
│       ├── models\
│       ├── pages\
│       ├── services\
│       └── widgets\    # (flat, NÃO tem lib\widgets\widgets\)
└── web\
    └── src\
        ├── api\        # activities.ts, auth.ts, client.ts, notifications.ts,
        │               # photos.ts, social.ts, stats.ts (getStatsByType — S14)
        ├── assets\
        ├── components\ # ActivityCard, ActivityResults, AppHeader,
        │               # CommentsSection, LikeButton, NotificationBell,
        │               # PeriodChart (NOVO S14 — unifica 4 gráficos),
        │               # PhotoGallery, PhotoUpload, ProtectedRoute,
        │               # RouteMap, StatsCards, UserResults
        ├── contexts\
        ├── hooks\      # useActivities, useActivitySearch, useAuth, useDebounce,
        │               # useNotifications, usePhotos, useProfile, useSocial,
        │               # useStats (useStatsByType — S14), useUserSearch
        ├── lib\        # format.ts, geo.ts
        ├── pages\      # ActivitiesPage, ActivityDetailPage, FeedPage,
        │               # LoginPage, NotificationsPage, ProfilePage,
        │               # RegisterPage, SearchPage, UploadPage
        └── types\      # api.ts (todos os tipos, StatsByType* — S14)

DIVERGÊNCIAS vs handoff da Sessão 13 (registrar para não errar):
- `web/src/components/` PERDEU 4 arquivos na Sessão 14:
  WeeklyChart.tsx, MonthlyChart.tsx, WeeklyActivitiesChart.tsx,
  MonthlyActivitiesChart.tsx. Foram unificados em `PeriodChart.tsx`.
  Se algum deles reaparecer no disco, é resquício — perguntar antes de mexer.

Se um arquivo específico for necessário, o pedido correto é:
    Get-Content -Encoding UTF8 <caminho completo>
E o script de descoberta (primeira ação de sessão) está na seção 6.

COMO RODAR COMANDOS FLUTTER NO WINDOWS DESTE USUÁRIO
-----------------------------------------------------
- Flutter instalado em: C:\Users\nasci\flutter (bin em ...\flutter\bin).
- Versões: Flutter 3.47.9 (stable) / Dart 3.13.7 / DevTools 2.60.0.
- PROBLEMA CONHECIDO: mesmo com C:\Users\nasci\flutter\bin no PATH do usuário
  e flutter.bat existindo, o PowerShell frequentemente NÃO reconhece o
  comando `flutter` — é cache de sessão do terminal/VS Code.
- SOLUÇÃO QUE FUNCIONA (usar por padrão):
      & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>
- Repo/repo mobile: D:\Rumo e D:\Rumo\mobile. PowerShell, Windows 5.1.

COMO RODAR DOCKER E PYTEST LOCAL (Windows deste usuário)
--------------------------------------------------------
- Docker Desktop instalado em:
    C:\Users\nasci\AppData\Local\Programs\DockerDesktop
- O executável `docker.exe` está em:
    C:\Users\nasci\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe
- Este caminho ESTÁ no PATH do usuário. Se `docker` não for reconhecido,
  é porque o PowerShell foi aberto de dentro do VS Code / Windows Terminal
  (herda PATH antigo). SOLUÇÃO: abrir PowerShell via Win+R → "powershell".
- Container de teste: `rumo_postgres_test` (5433). Containers permanentes
  `rumo-redis` (6379) e `rumo-postgres` (5432) NÃO são de teste.
- Passos para pytest local:
      1. PowerShell via Win+R → "powershell"
      2. `docker version` (Client + Server) e `docker compose version`
      3. `cd D:\Rumo\backend`
      4. `docker compose -f docker-compose.test.yml up -d`
      5. `docker ps` (rumo_postgres_test Up healthy na 5433)
      6. `.\.venv\Scripts\Activate.ps1` (prompt vira `(.venv)`)
      7. `pytest -q` — esperado: **118 passed** (verde ao fim da Sessão 14)
- Se `Activate.ps1` der erro de política:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

COMO TESTAR O BACKEND DE PRODUÇÃO SEM O APP (PowerShell)
--------------------------------------------------------
1) Login (retorna JWT):
     $body = "username=prod@rumo.com&password=senha12345"
     $login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
     $token = $login.access_token
2) Feed (com bbox):
     $feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=5" -Headers @{ Authorization = "Bearer $token" }
3) Track de uma atividade:
     $t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/track" -Headers @{ Authorization = "Bearer $token" }
4) Stats (todos validados em produção):
     Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
     Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
     Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/monthly?months=6" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
     Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
- Conta de teste: prod@rumo.com / senha12345.
- O endpoint /activities/stats/by-type EXISTE em produção e responde OK
  (validado na Sessão 14 — retornou { items: [...] } com other=3 e walk=3
  para a conta de teste).

O QUE O ASSISTENTE PRECISA PEDIR AO USUÁRIO (não tem acesso a arquivos)
-----------------------------------------------------------------------
- Conteúdo de arquivos via: Get-Content -Encoding UTF8 <caminho>
  (SEMPRE passar -Encoding UTF8; sem isso, acentos viram "inÃ­cio".)
- Saídas de comandos (flutter analyze, npm run build, git log, git status,
  pytest -q, ruff check).
- Nunca assumir estrutura "de cabeça": pedir o arquivo antes de reescrevê-lo.
- ATENÇÃO — arquivos truncados/duplicados: se um Get-Content vier com a
  última linha cortada OU com o conteúdo DUPLICADO (aconteceu na Sessão 14
  com tests/test_stats.py: o editor ANEXOU o conteúdo novo em vez de
  substituir, gerando F811 do Ruff), NÃO adivinhar o final. Pedir
  `ruff check <arquivo>` (lista todas as duplicatas de uma vez) e entregar
  o arquivo completo para o usuário fazer Ctrl+A → colar → salvar.
- ATENÇÃO — `git diff` pipeado no PowerShell pode exibir acentos como
  mojibake. É artefato de codepage do pipe, NÃO corrupção do arquivo.
- ATENÇÃO — `git log --oneline` no PowerShell às vezes cola a última linha
  com o prompt seguinte. Não é corrupção; é formatação.

ACORDOS DE TRABALHO (válidos em todas as sessões)
--------------------------------------------------
1. SEMPRE seguir a recomendação do assistente. Quando houver decisão
   pendente, executar a recomendada salvo instrução explícita em contrário.
   (O usuário reforçou isso no início da Sessão 14 e de novo no início da
   Sessão 15.)
2. SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff
   parcial, nunca "// resto igual". Preservar imports, comentários e trechos
   que já funcionam. Destacar o trecho alterado com comentário curto acima
   (// [Sessão N] ou // [Sessão N — fix]).
3. UMA versão por arquivo por resposta. Se errar no meio do raciocínio,
   cortar a versão errada e entregar só a corrigida com nota de 1 linha.
   NUNCA duas versões do mesmo arquivo na mesma resposta.
4. HANDOFF PREVENTIVO em ~70-80% do limite de contexto: parar o trabalho em
   curso e entregar o HANDOFF completo neste mesmo formato (seções 0 a 8),
   pronto para colar no próximo chat. Handoff deve ser COMPLETO e bem
   explicado, não resumido.

===============================================================================
1. TL;DR PARA QUEM CHEGA AGORA
===============================================================================

- Backend: 118 testes passando LOCALMENTE (pytest -q verde na Sessão 14).
  Antes da Sessão 13 era só produção; desde a 13 é local também (Docker
  Desktop + venv ativa + container de teste na 5433). Activity.route é
  PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com
  coordinates em ordem GeoJSON [lon, lat], bbox [minLon,minLat,maxLon,maxLat],
  n_points, simplified. Responde 404 quando route é NULL.
- ActivityResponse (feed/lista/detalhe/busca) inclui
  `bbox: list[float] | None`, calculado via ST_XMin/YMin/XMax/YMax do PostGIS
  no mesmo SELECT (sem N+1). `None` quando route é NULL.
- Endpoints de stats (todos validados em produção):
  * GET /activities/stats/summary — StatsSummary (totais gerais).
  * GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.
  * GET /activities/stats/monthly?months=N — StatsMonthlyResponse.
  * GET /activities/stats/by-type — StatsByTypeResponse (NOVO S14).
  Os 3 primeiros aceitam `activity_type` opcional como filtro. O by-type
  NÃO aceita filtro (o objetivo é ver todos os tipos lado a lado).
- Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet
  (RouteMap no detalhe) + recharts (gráficos no perfil).
- Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
  alternância Mapa/Satélite, miniatura estática no feed. Sem mudanças na S14.
- [Sessão 14 — entregas]
  * Rota A: 4 gráficos do perfil unificados em `PeriodChart.tsx`
    (parâmetros `period: "weekly"|"monthly"` × `metric: "distance"|"activities"`).
    Eliminou WeeklyChart, MonthlyChart, WeeklyActivitiesChart e
    MonthlyActivitiesChart. ProfilePage reduziu de 16.30 kB → 11.73 kB.
  * Rota B1: drill-down de stats por tipo de atividade.
    - Backend: `get_by_type` em stats_service.py; schemas
      StatsByTypeItem/StatsByTypeResponse; rota GET /activities/stats/by-type.
      7 testes novos (5 service + 2 rota) — 118 passed.
    - Web: tipos StatsByTypeItem/StatsByTypeResponse em types/api.ts;
      getStatsByType em api/stats.ts; useStatsByType em hooks/useStats.ts;
      tabela "Por tipo de atividade" em ProfilePage.tsx (abaixo do gráfico).
    - Validação em produção: endpoint respondeu other=3, walk=3 (ordenação
      por atividades DESC e desempate alfabético funcionando).

<!-- [Sessão 15] Entregas da Sessão 15 até o momento (em andamento): -->
- [Sessão 15 — entregas até agora]
  * Rota A(a) — silenciar warnings do fitparse: `pytest.ini` ganhou
    `filterwarnings = ignore::DeprecationWarning:fitparse\.processors`,
    apagando os 3611 warnings (2 únicos, deduplicados) do parsing de .FIT
    sem esconder warnings de outras libs (validado com `-W default::` no
    CLI: só os do fitparse voltaram). `tests/conftest.py` teve o bloco
    `warnings.filterwarnings` revertido (não funciona no pytest — o plugin
    reseta a lista antes de cada teste); a docstring foi mantida e
    atualizada para registrar a decisão e a dívida do fitdecode.
    Commit fa4fcc4.
  * Rota A(b) — coluna "Pace médio" no drill-down por tipo:
    `ProfilePage.tsx` ganhou a coluna (entre Tempo e Calorias), com regra
    `PACE_TYPES = {run, walk, hike}` → `formatPace()`, senão `"—"`. O pace
    é calculado no front (`total_duration_s / (total_distance_m / 1000)`),
    com guarda para `total_distance_m <= 0`. De brinde, foram removidas as
    duas funções inline duplicadas (`formatDistance`, `formatDuration`) que
    existiam desde a S14 — agora vêm de `lib/format.ts`. Isso alinha a
    tabela ao padrão pt-BR do resto do app (`3,2 km`, `1h 05min`).
    Commit 053239c.
  * Rota A(c) — documentar a decisão dos enums nativos do Postgres:
    este acréscimo no handoff (seção 7, "Armadilha conhecida"). Próximo
    commit, junto com esta atualização.

===============================================================================
2. PRODUÇÃO E AMBIENTE
===============================================================================

- Backend: https://rumo-api-5s0b.onrender.com
- Docs Backend: https://rumo-api-5s0b.onrender.com/docs
- Frontend Web: https://rumo-wheat.vercel.app
- Repo local: D:\Rumo
- Mobile: D:\Rumo\mobile
- Web: D:\Rumo\web (scripts: "build": "tsc -b && vite build", "lint": "eslint .")
- Flutter: 3.47.9 / Dart 3.13.7
- Docker Desktop: 4.93.0 (engine 29.8.1, compose v5.5.1)
- SO: Windows, PowerShell 5.1
- Venv backend: D:\Rumo\backend\.venv (ativa com .\.venv\Scripts\Activate.ps1)
- Git (estado ao fim da Sessão 15 — CONFIRMAR com git log + git status no
  início da Sessão 16):
    053239c  (HEAD -> main, origin/main) feat(web): coluna de pace medio no drill-down por tipo
    fa4fcc4  test(backend): silencia deprecation do fitparse via filterwarnings no pytest.ini
    31f6c6c  docs: handoff da Sessão 14
    c0ad55d  feat: drill-down de stats por tipo de atividade
    a27572c  refactor(web): unifica graficos do perfil em PeriodChart
- Todos os commits da Sessão 15 estão em origin/main (pushados).
- Render e Vercel deployam automático a cada push em main. O endpoint
  /activities/stats/by-type já está no ar e foi validado em produção na S14.

===============================================================================
3. O QUE FOI FEITO NA SESSÃO 14
===============================================================================

3.1 Validação de estado inicial (Sessão 14)
    - Push OK (origin/main em 3474d9b).
    - Working tree limpo.
    - npm run build verde (827 modules, 3.34s).
    - flutter analyze: No issues found (60.1s).
    - docker version OK, compose v5.5.1 OK.
    - rumo_postgres_test Up healthy na 5433.
    - pytest -q: 111 passed.
    - Descoberta de estrutura via Get-ChildItem — sem divergências vs handoff
      da Sessão 13.

3.2 [Web] Rota A — unificar 4 gráficos em PeriodChart
    - Lidos os 4 arquivos: WeeklyChart, MonthlyChart, WeeklyActivitiesChart,
      MonthlyActivitiesChart (~85% idênticos, diferenças: label X, tooltip,
      título, dataKey, allowDecimals, domain do eixo Y).
    - Criado components/PeriodChart.tsx parametrizado por
      (period × metric). Encapsula: loading, erro, vazio, label X
      (DD/MM vs MM/YYYY), título, conversão km, yMax dinâmico,
      allowDecimals, tooltip formatado, cor/dot/altura.
    - ProfilePage.tsx: 4 condições explícitas → 1 chamada parametrizada.
    - Tipos ChartPeriod/ChartMetric exportados do próprio PeriodChart
      (ProfilePage importa direto, sem duplicar union types).
    - FIX de tipos do TypeScript na Sessão 14:
      * `domain={[0, yMax]}` — yMax passou a ser `number | null` e domain
        vira `[0, yMax]` só quando `!== null`. O tipo `AxisDomain` do recharts
        não aceita `[number, number | undefined]`.
      * `formatter` — recharts tipa `value` como `ValueType | undefined`;
        assinatura passou a aceitar `unknown` e fazer `Number(value ?? 0)`.
    - Validação em produção: 4 combinações OK (usuário confirmou).
    - 4 arquivos antigos removidos. Commit: a27572c.
    - Resultado: ProfilePage 16.30 kB → 11.73 kB (−4.57 kB), build 3.34s→2.03s.

3.3 [Backend] Rota B1 — drill-down por tipo de atividade
    - schemas/stats.py: +StatsByTypeItem, +StatsByTypeResponse.
    - services/stats_service.py: +get_by_type (GROUP BY activity_type).
    - routers/activities.py: +GET /stats/by-type (declarado depois de
      /stats/monthly e antes de /{activity_id}).
    - tests/test_stats.py: +7 testes.
      * FALHA inicial: `test_get_by_type_tie_breaks_by_type_asc` e
        `test_route_by_type_shape` esperavam "cycle" antes de "run"
        (desempate alfabético), mas o SQL devolveu "run" antes de "cycle".
      * CAUSA: `Activity.activity_type` é Enum NATIVO do Postgres, e ORDER BY
        em coluna Enum ordena pela ORDEM DE DECLARAÇÃO do tipo, não pela
        string. A ordem declarada é (run, walk, cycle, hike, swim, other).
      * FIX: removido tie-break do SQL; ordenação final em Python com
        `items.sort(key=lambda r: (-r["total_activities"], r["activity_type"]))`.
        Universo é ≤ 6 linhas → custo irrelevante, comportamento previsível,
        desacoplado do enum nativo. Comentário explicativo no código.
      * Resultado: 118 passed (111 originais + 7 novos).

3.4 [Web] Rota B1 — tabela por tipo no ProfilePage
    - types/api.ts: +StatsByTypeItem, +StatsByTypeResponse.
    - api/stats.ts: +getStatsByType() (sem params — o backend já ordena).
    - hooks/useStats.ts: +statsKeys.byType(), +useStatsByType(enabled).
    - pages/ProfilePage.tsx: +seção "Por tipo de atividade" abaixo do gráfico.
      Tabela com Tipo | Atividades | Distância | Tempo | Calorias.
      Helper formatDistance (m se < 1000, km com 1 decimal se >= 1000) e
      formatDuration (Xh Ymin se >= 1h, senão Ymin) — inline porque só essa
      tabela usa. TYPE_LABELS mapeia enum → pt-BR.
      byTypeQuery usa isSelf como enabled (não aparece em perfis de terceiros).
    - Build: 824 modules (era 827), ProfilePage 11.73 kB → 14.03 kB.

3.5 Validação em produção (B1)
    - Endpoint GET /activities/stats/by-type na conta prod@rumo.com retornou:
        items: [
          { activity_type: "other", total_activities: 3, total_distance_m: 10800.0, ... },
          { activity_type: "walk",  total_activities: 3, total_distance_m: 15643.22, ... }
        ]
    - Ordenação: other < walk no empate (alfabético ASC) — CONFIRMADO em prod.
    - Valores de calories/duration/elevation consistentes com o summary.

3.6 Estado final da sessão
    - Working tree limpo, main == origin/main == c0ad55d.
    - npm run build: verde (824 modules).
    - pytest -q: 118 passed (local).
    - ruff check tests/test_stats.py: All checks passed.

===============================================================================
4. CONTRATOS DO BACKEND RELEVANTES (referência)
===============================================================================

- GET /activities/{id}/track  (auth: Bearer JWT)
  Permissão: dono OU seguidor do dono (404 caso contrário).
  404 quando activity.route is None → detail "Atividade não possui rota".
  Resposta (TrackResponse):
    {
      "activity_id": "uuid",
      "type": "LineString",
      "coordinates": [[lon, lat], [lon, lat], ...],  // GeoJSON
      "bbox": [minLon, minLat, maxLon, maxLat],
      "n_points": 60,
      "simplified": false
    }

- ActivityResponse (feed/lista/detalhe/busca):
    {
      ...,
      "bbox": [minLon, minLat, maxLon, maxLat]  // ou null
    }
  Ordem GeoJSON. Null quando route IS NULL. Sem N+1.

- ActivityResponse NÃO inclui route nem coordinates (polyline só via /track).

- GET /activities/stats/summary?activity_type=<opcional>
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

- GET /activities/stats/weekly?weeks=N&activity_type=<opcional>
  → StatsWeeklyResponse:
    {
      "weeks": 8,
      "items": [
        {
          "period_start": "2026-11-02",  // sempre segunda-feira
          "total_activities": 1,
          "total_distance_m": 1000.0,
          "total_duration_s": 600,
          "total_calories": 41
        },
        ...
      ]
    }

- GET /activities/stats/monthly?months=N&activity_type=<opcional>
  → StatsMonthlyResponse: mesmo shape do weekly, mas period_start é sempre
  o primeiro dia do mês ("YYYY-MM-01") e a chave é "months".

- GET /activities/stats/by-type  (NOVO S14 — sem query params)
  → StatsByTypeResponse:
    {
      "items": [
        {
          "activity_type": "run",  // string ("run", "walk", "cycle", "hike", "swim", "other")
          "total_activities": 12,
          "total_distance_m": 84000.0,
          "total_duration_s": 25200,
          "total_elevation_gain_m": 1200.0,
          "total_calories": 4200
        },
        ...
      ]
    }
  Só tipos com >= 1 atividade aparecem. Ordenação final garantida:
  total_activities DESC, activity_type ASC (aplicado em Python, não no SQL).
  Decisão técnica registrada: enums nativos do Postgres ordenam pela ordem de
  DECLARAÇÃO, não pela string; o sort em Python elimina esse acoplamento.

- Todos os endpoints de stats são do current_user (não aceitam user_id).
  A UI só mostra stats no próprio perfil (isSelf).

===============================================================================
5. COMMITS PENDENTES / ESTADO DO REPO
===============================================================================

<!-- [Sessão 15] Bloco atualizado: A(a) e A(b) já pushadas; A(c) neste commit. -->
- Sessões 9, 10, 11, 12, 13, 14 e 15 (parcial) commitadas e pushadas.
- origin/main == main == HEAD no momento do commit desta atualização
  (fa4fcc4 → 053239c → este commit de docs).
- A(a) commit fa4fcc4: silencia warnings do fitparse via pytest.ini.
- A(b) commit 053239c: coluna de pace médio no drill-down por tipo.
- A(c) (este commit): documenta a armadilha dos enums nativos + atualiza
  o handoff com o que a Sessão 15 produziu até agora.
- Nenhuma pendência conhecida de git.

===============================================================================
6. SCRIPTS ÚTEIS (PowerShell)
===============================================================================

# [Sessão 15 — primeira ação] Abrir PowerShell via Win+R → "powershell"
# (NÃO abrir de dentro do VS Code / Windows Terminal)
# Depois:

# [Sessão 15 — primeira ação] Descoberta da estrutura do repo
cd D:\Rumo
Get-ChildItem -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend\app\routers -File | Select-Object Name
Get-ChildItem D:\Rumo\backend\tests -File | Select-Object Name

# [Sessão 15 — primeira ação] Estado do repo
cd D:\Rumo
git push
git log --oneline -5
git status --short

# [Sessão 15 — primeira ação] Sanidade de build
cd D:\Rumo\web
npm run build

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

# [Sessão 15 — primeira ação] Docker + pytest local
docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps
.\.venv\Scripts\Activate.ps1
pytest -q

# Login (produção)
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token

# Feed com bbox (produção)
$feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=5" -Headers @{ Authorization = "Bearer $token" }
$feed | ForEach-Object { Write-Host "id=$($_.id.Substring(0,8))  title=$($_.title)  bbox=$($_.bbox -join ',')" }

# Stats (produção)
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/monthly?months=6" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/by-type" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3

# Track (produção)
$t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/track" -Headers @{ Authorization = "Bearer $token" }

# Build web
cd D:\Rumo\web
npm run build

# Flutter analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

# Ruff (backend)
cd D:\Rumo\backend
.\.venv\Scripts\Activate.ps1
ruff check .

===============================================================================
7. DÍVIDAS TÉCNICAS
===============================================================================

- (RESOLVIDA na Sessão 14) Quatro gráficos quase idênticos no perfil
  (~85% de duplicação). Unificados em PeriodChart.tsx parametrizado por
  (period × metric). Commit a27572c.

<!-- [Sessão 15] Item abaixo reescrito: era "dívida em aberto", virou
"armadilha conhecida" com decisão tomada e regra acionável. -->
- (ARMADILHA CONHECIDA — decisão tomada na Sessão 14, documentada na S15)
  Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO, não pela
  string. `Activity.activity_type` é Enum nativo com ordem declarada
  (run, walk, cycle, hike, swim, other). Portanto, `ORDER BY activity_type`
  no SQL devolve nessa ordem — não em ordem alfabética.
  DECISÃO: para `get_by_type` (stats_service.py), o desempate final é feito
  em Python com
      items.sort(key=lambda r: (-r["total_activities"], r["activity_type"]))
  Justificativa: universo ≤ 6 linhas → custo irrelevante, comportamento
  previsível, desacoplado do enum nativo. Há comentário explicativo no
  código.
  REGRA PARA O FUTURO: qualquer novo `ORDER BY` em coluna Enum DEVE
  (a) fazer o sort final em Python, ou (b) ser explicitamente testado
  contra a ordem de declaração do enum. Não confiar em ORDER BY direto
  em coluna Enum. Se um dia for trocar enums nativos por VARCHAR+check no
  banco, esta regra some — mas a migração é de baixa prioridade e não
  deve ser feita sem necessidade.

<!-- [Sessão 15] Item abaixo marcado como RESOLVIDO. -->
- (RESOLVIDA na Sessão 15) Warnings do fitparse (biblioteca externa) durante
  pytest: `datetime.utcfromtimestamp() is deprecated`. Eram 3611 warnings
  brutos (2 únicos, deduplicados) em tests/test_calories.py.
  RESOLUÇÃO: filtro em `pytest.ini`:
      filterwarnings =
          ignore::DeprecationWarning:fitparse\.processors
  Cirúrgico por módulo — não esconde warnings de outras libs (validado com
  `-W default::` no CLI: só os do fitparse voltaram). Commit fa4fcc4.
  DÍVIDA REMANESCENTE: a correção real é migrar de fitparse (última release
  1.2.0, de 2020, dormente) para fitdecode (ativo, mantido, sem
  utcfromtimestamp). Reescreve o parsing de .FIT no upload e os testes de
  calorias. Merece sessão dedicada. Quando migrar, remover o filtro do
  pytest.ini.

- Web: miniatura do feed usa 1 tile OSM centralizado (bbox grande pode
  cortar bordas). Aceitável; se virar problema, evoluir para mosaico 2×2
  ou staticmap.openstreetmap.de.

- Mobile: sem inclinação/rotação 3D (flutter_map é 2D). Se 3D for
  requisito, avaliar maplibre_gl (decisão maior, pesada).

- TimeoutException do app mobile não reproduzido desde a Sessão 9.
  Registrar se voltar (tela + log do flutter run).

- (Oportunidade) RouteMap.tsx é reutilizável em qualquer página que
  renderize uma rota. Hoje só é usado em ActivityDetailPage. Se aparecer
  um segundo uso, considerar React.lazy() para tirar o leaflet (163 kB)
  do chunk da página que não mostra mapa. Ganho hoje é marginal (leaflet
  já está em chunk separado por conta do bundle splitting do Vite).

<!-- [Sessão 15] Item abaixo: "Coluna Pace médio" foi entregue (A-b).
O restante (filtro por período) continua como oportunidade. -->
- (OPORTUNIDADE) Drill-down de stats por tipo poderia ganhar, no futuro:
  * (RESOLVIDO na Sessão 15) Coluna "Pace médio". Implementada em
    ProfilePage.tsx com regra `PACE_TYPES = {run, walk, hike}`;
    `cycle/swim/other` mostram "—". Cálculo no front
    (`total_duration_s / (total_distance_m / 1000)`), com guarda para
    `total_distance_m <= 0`. De brinde, removidas as duas funções inline
    duplicadas (`formatDistance`, `formatDuration`) que a S14 tinha
    deixado no arquivo — agora vêm de `lib/format.ts`. Commit 053239c.
  * Filtro por período (ex.: "últimos 90 dias"). Hoje mostra "todos os
    tempos" — o que é o que o usuário quer no drill-down, mas vale
    considerar se surgir demanda.

- (Oportunidade) Stats no perfil: /activities/stats/summary, /weekly,
  /monthly e /by-type são só do current_user. Se um dia o requisito for
  "ver stats de outro usuário", precisa de novos endpoints (com
  privacidade, provavelmente via follow).

===============================================================================
8. PRÓXIMOS PASSOS RECOMENDADOS (Sessão 15 e além)
===============================================================================

<!-- [Sessão 15] Bloco atualizado: primeira ação já cumprida; Rota A(a) e
A(b) já entregues; sobra A(c) (este commit) e depois Rota B. -->

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 16 (antes de qualquer mudança de código):
  1) No terminal (PowerShell via Win+R → "powershell"):
        cd D:\Rumo
        git push
        git log --oneline -5
        git status --short
        cd web ; npm run build
        cd ..\mobile
        & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
     Confirmar com o usuário: push aceito, HEAD == origin/main, build e
     analyze verdes, working tree limpo.
  2) DOCKER + PYTEST LOCAL:
        docker version
        docker compose version
        cd D:\Rumo\backend
        docker compose -f docker-compose.test.yml up -d
        docker ps
        .\.venv\Scripts\Activate.ps1
        pytest -q
     Esperado: 118 passed, 0 warnings (graças ao filtro do pytest.ini).
  3) DESCOBERTA DE ESTRUTURA (obrigatória — não adivinhar):
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

ESTADO DA ROTA A (Sessão 15):
  (a) fitparse warnings → FEITO (fa4fcc4).
  (b) Pace médio no drill-down → FEITO (053239c).
  (c) Documentar decisão dos enums → FEITO (este commit).
  Rota A fechada. Sugestões de continuação abaixo.

ROTA A+ — Continuar o padrão "deixar o repo melhor do que estava"
  Sugestões de baixo risco para as próximas sessões:
    a) Migrar fitparse → fitdecode (elimina o filtro do pytest.ini e a
       dependência dormente). Requer: ler o código de parsing de .FIT
       (provavelmente em backend/app/services/ ou no router de upload),
       ler tests/test_calories.py, escolher API do fitdecode, reescrever,
       rodar pytest completo. Sessão dedicada.
    b) Adicionar coluna "Elevação" (ou "Elev. gain") no drill-down por tipo.
       O dado já está no contrato (`total_elevation_gain_m`), só falta
       exibir. Custo: 1 linha no header + 1 na linha + formatador
       (`formatElevation`? reusar `formatDistance`? decidir).
    c) Documentar no `docs/HANDOFF.md` (ou num futuro README) as rotas de
       API em formato de "cheat sheet" (hoje a seção 4 já cobre, mas é
       verbose — um sumário de 1 linha por endpoint ajudaria).

ROTA B — Feature nova (requer escolha com o usuário)
  Escopo médio-grande. Exemplos:
    - Stats "públicas" em perfis de terceiros (com privacidade via follow).
      Backend: novos endpoints com user_id + regra de follow.
    - Comparação "este período vs. anterior" em cada gráfico.
      Backend: adicionar campos `*_previous` em StatsWeeklyResponse/
      StatsMonthlyResponse (mexe em contrato — decidir antes).
    - Filtro de período no drill-down por tipo (90d, 1a, all).
      Backend: novo param em /stats/by-type.
    - Export de atividades (CSV/GPX). Fora do escopo mobile/web atual.
  Requer: desenhar contrato + schema + teste (validável localmente, com
  pytest verde) + UI no front.

  A minha recomendação para a Sessão 16 é a ROTA A+ (a ou b, nesta ordem
  de preferência). A Sessão 15 foi de consolidação — terminou limpa, com
  0 warnings no pytest e uma armadilha documentada. A dívida do fitdecode
  é a próxima "pedra no sapato" real; a coluna de elevação é ganho visível
  com custo de 10 minutos. Se o usuário preferir feature nova, Rota B é
  viável — mas o assistente deve explicitar que está adiando dívidas.

  Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes do
  fim, parar e entregar o HANDOFF completo da Sessão 16 neste mesmo formato
  (seções 0 a 8).