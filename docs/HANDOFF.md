===============================================================================
HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 13
===============================================================================

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
Sessões anteriores perderam tempo precioso porque o assistente tentou
"adivinhar" a árvore de diretórios e errou. Não repetir.

O QUE É LOCAL vs O QUE É PRODUÇÃO
----------------------------------
- LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI
  + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 +
  TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter).
  O assistente NÃO tem acesso a esses arquivos neste chat — o usuário precisa
  colar conteúdo de arquivos e saídas de terminal. Não assumir que o
  assistente consegue "ver" pastas.
- PRODUÇÃO (na nuvem, acessível por HTTP): backend no Render
  (https://rumo-api-5s0b.onrender.com), frontend web na Vercel
  (https://rumo-wheat.vercel.app). O backend de produção usa Postgres/PostGIS
  gerenciado (não é o local). Testar via HTTP é sempre possível.
- DOCKER: AGORA INSTALADO E FUNCIONAL no Windows local. `pytest -q` local
  verde (111 passed). Container de teste `rumo_postgres_test` na porta 5433.
  Para reativar numa sessão nova: (1) abrir Docker Desktop e esperar a
  baleia verde; (2) garantir que o terminal foi aberto via Win+R (fora do
  VS Code / Windows Terminal, que herdam PATH antigo); (3) `docker compose
  -f docker-compose.test.yml up -d`; (4) `pytest -q`.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)
--------------------------------------------------------------------
Árvore de alto nível REAL, confirmada no início da Sessão 13:

D:\Rumo\
├── .vscode\
├── backend\
│   ├── .pytest_cache\
│   ├── .ruff_cache\
│   ├── .venv\          # virtualenv Python ativo (Ativar com .\.venv\Scripts\Activate.ps1)
│   ├── alembic\
│   ├── app\
│   │   ├── core\
│   │   ├── models\
│   │   ├── routers\    # <-- aqui ficam os endpoints (activities.py, auth.py,
│   │   │               #     comments.py, feed.py, notifications.py,
│   │   │               #     photos.py, users.py). NÃO é "app/api/".
│   │   ├── schemas\
│   │   ├── services\
│   │   └── __pycache__\
│   ├── samples\
│   ├── scripts\
│   ├── tests\          # conftest.py + test_calories.py + test_comment.py +
│   │                   # test_follow.py + test_like.py + test_stats.py
│   ├── _scratch\       # rascunho (não mexer sem pedido)
│   └── docker-compose.test.yml
├── docs\
│   └── HANDOFF.md      # este arquivo
├── mobile\
│   └── lib\
│       ├── models\
│       ├── pages\
│       ├── services\
│       └── widgets\    # (NÃO tem lib\widgets\widgets\; é flat)
└── web\
    └── src\
        ├── api\        # activities.ts, auth.ts, client.ts, notifications.ts,
        │               # photos.ts, social.ts, stats.ts
        ├── assets\
        ├── components\ # ActivityCard, AppHeader, CommentsSection, LikeButton,
        │               # MonthlyActivitiesChart (NOVO S13),
        │               # MonthlyChart (NOVO S13), NotificationBell,
        │               # PhotoGallery, PhotoUpload, ProtectedRoute,
        │               # RouteMap (NOVO S13), StatsCards,
        │               # UserResults, WeeklyActivitiesChart (NOVO S13),
        │               # WeeklyChart, ActivityResults
        ├── contexts\
        ├── hooks\      # useActivities, useActivitySearch, useAuth, useDebounce,
        │               # useNotifications, usePhotos, useProfile, useSocial,
        │               # useStats, useUserSearch
        ├── lib\        # format.ts, geo.ts
        ├── pages\      # ActivitiesPage, ActivityDetailPage, FeedPage,
        │               # LoginPage, NotificationsPage, ProfilePage,
        │               # RegisterPage, SearchPage, UploadPage
        └── types\      # api.ts (todos os tipos, único arquivo)

DIVERGÊNCIAS vs handoff da Sessão 12 (registrar para não errar):
- Backend NÃO tem "app/api/". É "app/routers/".
- Web TEM "api/", "assets/", "contexts/" no src (não estavam listados antes).
- Backend TEM "_scratch/" (não estava listado antes).

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

COMO RODAR DOCKER E PYTEST LOCAL (Windows deste usuário) — NOVO NA SESSÃO 13
----------------------------------------------------------------------------
- Docker Desktop instalado em:
    C:\Users\nasci\AppData\Local\Programs\DockerDesktop
- O executável `docker.exe` está em:
    C:\Users\nasci\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe
- Este caminho ESTÁ no PATH do usuário (confirmado). Se o `docker` não for
  reconhecido numa sessão nova, é porque o PowerShell foi aberto de dentro
  do VS Code / Windows Terminal (herda PATH antigo). SOLUÇÃO:
      1. Fechar tudo. Abrir PowerShell via Win+R → "powershell" (filho
         direto do Explorer, lê o PATH atualizado).
      2. Confirmar: `docker version` (Client + Server) e
         `docker compose version` (v5.5.1 na Sessão 13).
      3. `cd D:\Rumo\backend`
      4. `docker compose -f docker-compose.test.yml up -d`
      5. `docker ps` (container `rumo_postgres_test` Up healthy na 5433)
      6. `.\.venv\Scripts\Activate.ps1` (prompt vira `(.venv)`)
      7. `pytest -q` — esperado: **111 passed** (verde na Sessão 13)
- NOTA: no Windows local também existem containers permanentes
  `rumo-redis` (6379) e `rumo-postgres` (5432), que NÃO são de teste.
  O de teste é o `rumo_postgres_test` (5433). Não confundir.
- Se `Activate.ps1` der erro de política de execução:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  antes de tentar de novo (só afeta a sessão atual).

COMO TESTAR O BACKEND DE PRODUÇÃO SEM O APP (PowerShell)
--------------------------------------------------------
1) Login (retorna JWT):
     $body = "username=prod@rumo.com&password=senha12345"
     $login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
     $token = $login.access_token
2) Feed (com bbox):
     $feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=5" -Headers @{ Authorization = "Bearer $token" }
     $feed | ForEach-Object { Write-Host "id=$($_.id.Substring(0,8))  title=$($_.title)  bbox=$($_.bbox -join ',')" }
3) Track de uma atividade:
     $id = "UUID"
     $t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/track" -Headers @{ Authorization = "Bearer $token" }
     Write-Host "n=$($t.n_points) bbox=$($t.bbox -join ',')"
4) Stats (validado na Sessão 13):
     Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
     Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/weekly?weeks=8" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
     Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/stats/monthly?months=6" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
- Conta de teste: prod@rumo.com / senha12345.
- O endpoint /activities/stats/monthly EXISTE em produção e responde OK
  (validado na Sessão 13). O tipo StatsMonthlyResponse no front estava
  correto, só não era consumido — agora é.

O QUE O ASSISTENTE PRECISA PEDIR AO USUÁRIO (não tem acesso a arquivos)
-----------------------------------------------------------------------
- Conteúdo de arquivos específicos via: Get-Content -Encoding UTF8 <caminho>
  (SEMPRE passar -Encoding UTF8; sem isso, acentos viram "inÃ­cio".)
- Saídas de comandos (flutter analyze, npm run build, git log, git status,
  pytest -q).
- Nunca assumir estrutura de pastas "de cabeça": pedir o arquivo antes de
  reescrevê-lo, para não quebrar o que já funciona.
- ATENÇÃO — arquivos truncados: se um Get-Content vier com a última linha
  cortada (ex.: "upda"), o arquivo está corrompido no disco. NÃO adivinhar o
  final. Pedir `git status --short -- <arquivo>`; se estiver " M", rodar
  `git checkout -- <arquivo>` e recuperar do HEAD.
- ATENÇÃO — `git diff` pipeado no PowerShell pode exibir acentos como
  mojibake (ex.: "Sess笏愿ｺo"). É artefato de codepage do pipe, NÃO corrupção
  do arquivo. Usar `Get-Content -Encoding UTF8` para inspecionar o conteúdo
  real antes de qualquer decisão sobre o arquivo.
- ATENÇÃO — `git log --oneline` no PowerShell às vezes cola a última linha
  com o prompt seguinte (ex.: "bc0b9d9 feat(...) PS D:\Rumo>"). Não é
  corrupção; é só formatação. Ler com calma.

ACORDOS DE TRABALHO (válidos em todas as sessões)
--------------------------------------------------
1. SEMPRE seguir a recomendação do assistente. Quando houver decisão
   pendente, executar a recomendada salvo instrução explícita em contrário.
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

- Backend: 111 testes passando LOCALMENTE (pytest -q verde na Sessão 13).
  Antes da Sessão 13, era só produção; agora é local também (Docker Desktop
  + venv ativa + container de teste na 5433). Activity.route é PostGIS
  LINESTRING. GET /activities/{id}/track devolve TrackResponse com
  coordinates em ordem GeoJSON [lon, lat], bbox [minLon,minLat,maxLon,maxLat],
  n_points, simplified. Responde 404 quando route é NULL. Acesso: dono OU
  seguidor do dono.
- ActivityResponse (feed/lista/detalhe/busca) inclui
  `bbox: list[float] | None`, calculado via ST_XMin/YMin/XMax/YMax do PostGIS
  no mesmo SELECT (sem N+1). `None` quando route é NULL.
- Endpoints de stats (todos validados em produção):
  * GET /activities/stats/summary — StatsSummary (totais gerais).
  * GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.
  * GET /activities/stats/monthly?months=N — StatsMonthlyResponse.
  Todos aceitam `activity_type` opcional como filtro.
- Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet
  (RouteMap no detalhe) + recharts (gráficos no perfil).
- Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
  alternância Mapa/Satélite, miniatura estática no feed.
- [Sessão 13 — entregas]
  * Docker Desktop funcional no Windows local + pytest -q local verde (111
    passed). O caminho do docker.exe foi adicionado ao PATH (já estava, na
    verdade — o problema era abrir PowerShell fora do VS Code/Windows
    Terminal para ler o PATH atualizado).
  * Web: toggle Semanal | Mensal no gráfico de evolução do perfil.
    MonthlyChart.tsx (novo), getStatsMonthly em api/stats.ts,
    useStatsMonthly em hooks/useStats.ts.
  * Web: RouteMap.tsx extraído do ActivityDetailPage. Encapsula Leaflet,
    Polyline, FitBounds, toggle Mapa/Satélite e o estado vazio ("Sem rota
    disponível"). ActivityDetailPage ficou ~50 linhas mais enxuto e usa
    `<RouteMap track={track} className="mb-6" />`.
  * Web: segundo toggle Distância | Atividades no perfil. WeeklyActivities-
    Chart.tsx e MonthlyActivitiesChart.tsx (novos). ProfilePage gerencia
    dois eixos independentes: chartMode ("weekly" | "monthly") e
    chartMetric ("distance" | "activities"). 4 combinações, zero request
    nova (StatsPeriod já tem total_activities e total_distance_m).

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
- Git (estado ao fim da Sessão 13 — CONFIRMAR com git log + git status no
  início da Sessão 14):
    <hash-F>  (HEAD -> main, origin/main) feat(web): segundo gráfico de atividades por período no perfil
    b8f5a13   refactor(web): extrai RouteMap do ActivityDetailPage
    e3c564b   feat(web): toggle Semanal/Mensal no gráfico de evolução do perfil
    24b3fac   docs: handoff da Sessão 12
    894e4b5   docs: handoff da Sessão 11 (toggle Mapa/Satélite, miniaturas, bbox)
    bc0b9d9   feat(web): toggle Mapa/Satélite no mapa do detalhe (igual mobile)
- Todos os commits da Sessão 13 estão em origin/main (pushados).
- ATENÇÃO: o hash-F (feature F) será preenchido com o valor real do
  git log --oneline -1 após o commit. Se a Sessão 14 começar e o hash não
  aparecer aqui, PEDIR o git log ao usuário.

===============================================================================
3. O QUE FOI FEITO NA SESSÃO 13
===============================================================================

3.1 Validação de estado e fechamento do handoff da Sessão 12
    - Push inicial OK (origin/main em 894e4b5).
    - docs/HANDOFF.md commitado como 24b3fac ("docs: handoff da Sessão 12").
    - Working tree limpo.
    - Descoberta de estrutura via Get-ChildItem (obrigatória — ver seção 6).

3.2 Desbloqueio do Docker (dívida mais antiga)
    - Docker Desktop já estava instalado em
      C:\Users\nasci\AppData\Local\Programs\DockerDesktop (não no caminho
      padrão C:\Program Files\Docker).
    - O problema NÃO era PATH (já estava correto). Era sessão do PowerShell
      aberta de dentro do VS Code / Windows Terminal, herdando PATH antigo
      que não enxergava o docker.exe.
    - Solução: abrir PowerShell via Win+R → "powershell" (filho direto do
      Explorer, lê o PATH atualizado).
    - `docker version` (Client + Server + Engine) OK. `docker compose version`
      v5.5.1 OK.
    - Container `rumo_postgres_test` Up healthy na 5433.
    - `.\.venv\Scripts\Activate.ps1` ativa a venv. `pytest -q` = **111
      passed in 34.63s** (com 3611 warnings do fitparse — não quebram).
    - DÍVIDA FECHADA.

3.3 [Web] Toggle Semanal/Mensal no perfil
    - Backend: /activities/stats/monthly?months=N confirmado em produção
      (responde 200 com StatsMonthlyResponse).
    - api/stats.ts: nova função getStatsMonthly(months, params).
    - hooks/useStats.ts: novo hook useStatsMonthly(months, activityType,
      enabled), nova chave statsKeys.monthly(...).
    - components/MonthlyChart.tsx (novo): espelho do WeeklyChart, eixo X
      MM/YYYY, tooltip "Mês de MM/YYYY".
    - pages/ProfilePage.tsx: estado chartMode ("weekly" | "monthly"),
      toggle visual, render condicional. monthlyQuery lazy via
      `enabled: isSelf && chartMode === "monthly"`.
    - Commit: e3c564b.

3.4 [Web] Extração do RouteMap
    - components/RouteMap.tsx (novo): recebe track (TrackResponse |
      undefined), height (default "24rem") e className (default "").
      Encapsula: TileLayer OSM ↔ Esri, Polyline, FitBounds, toggle
      Mapa/Satélite e o estado vazio ("Sem rota disponível pra esta
      atividade."). Comportamento idêntico ao bloco inline anterior.
    - pages/ActivityDetailPage.tsx: bloco inline do mapa removido; usa
      `<RouteMap track={track} className="mb-6" />`. Imports de
      react-leaflet/leaflet removidos. Import de useState do react também
      removido (o estado `satelite` foi para dentro do RouteMap).
    - Validação em produção OK (polyline, toggle, fit bounds, estado vazio).
    - Commit: b8f5a13.

3.5 [Web] Segundo gráfico: Atividades × Distância
    - components/WeeklyActivitiesChart.tsx (novo): eixo Y = contagem de
      atividades (inteiro), domain dinâmico (mínimo 5), allowDecimals=false,
      tooltip com pluralização ("1 atividade" / "N atividades").
    - components/MonthlyActivitiesChart.tsx (novo): idem mensal, eixo X
      MM/YYYY, tooltip "Mês de MM/YYYY".
    - pages/ProfilePage.tsx: estado chartMetric ("distance" | "activities"),
      segundo toggle visual (inline-flex, mesmo padrão do primeiro), 4
      condições explícitas no render (chartMode × chartMetric), zero request
      nova (weeklyQuery/monthlyQuery já trazem total_activities).
    - Validação em produção OK (4 combinações).
    - Commit: <hash-F> (ver seção 2).

3.6 Estado final da sessão
    - Working tree limpo, main == origin/main.
    - npm run build: verde (827 modules, ProfilePage 16.30 kB / gzip 3.56).
    - flutter analyze: no início da sessão verde (45.7s; sem mudanças no
      mobile na Sessão 13).
    - pytest -q: 111 passed (local).

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
  Ordem GeoJSON. Null quando route IS NULL. Sem N+1, via 4 funções PostGIS
  no SELECT.

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
          "period_start": "2026-11-02",
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
  o primeiro dia do mês ("YYYY-MM-01") e a chave é "months". Validado na
  Sessão 13.

- Todos os endpoints de stats são do current_user (não aceitam user_id).
  A UI só mostra stats no próprio perfil (isSelf).

===============================================================================
5. COMMITS PENDENTES / ESTADO DO REPO
===============================================================================

- Sessões 9, 10, 11, 12 e 13 commitadas e pushadas.
- origin/main == main == HEAD no fim da Sessão 13.
- docs/HANDOFF.md desta Sessão 13 deve substituir o anterior no início da
  Sessão 14 e ser commitado como `docs: handoff da Sessão 13` (1 commit
  adicional, junto ou após o push inicial da Sessão 14).
- Nenhuma pendência conhecida de git.

===============================================================================
6. SCRIPTS ÚTEIS (PowerShell)
===============================================================================

# [Sessão 14 — primeira ação] Abrir PowerShell via Win+R → "powershell"
# (NÃO abrir de dentro do VS Code / Windows Terminal, para ler o PATH atual)
# Depois:

# [Sessão 14 — primeira ação] Descoberta da estrutura do repo
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

# [Sessão 14 — primeira ação] Estado do repo
cd D:\Rumo
git push
git log --oneline -5
git status --short

# [Sessão 14 — primeira ação] Sanidade de build
cd D:\Rumo\web
npm run build

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

# [Sessão 14 — primeira ação] Docker + pytest local
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

# Track (produção)
$t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/track" -Headers @{ Authorization = "Bearer $token" }

# Build web
cd D:\Rumo\web
npm run build

# Flutter analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

===============================================================================
7. DÍVIDAS TÉCNICAS
===============================================================================

- (RESOLVIDO na Sessão 13) Docker Desktop não instalado / pytest local não
  rodava. Agora `pytest -q` local está verde (111 passed). O caminho do
  docker.exe é C:\Users\nasci\AppData\Local\Programs\DockerDesktop\resources\bin
  e está no PATH do usuário. Para reativar em sessão nova: abrir PowerShell
  via Win+R → "powershell" (NÃO de dentro do VS Code / Windows Terminal).

- (NOVO na Sessão 13) Quatro gráficos quase idênticos no perfil:
  WeeklyChart, MonthlyChart, WeeklyActivitiesChart, MonthlyActivitiesChart.
  ~85% de código duplicado (wrapper, eixos, tooltip, dot, altura). Próximo
  passo natural: extrair `<PeriodChart metric="distance" | "activities"
  period="weekly" | "monthly" />` e reduzir o ProfilePage em ~3 kB.
  Não fazer em cima da hora — exige validação visual das 4 combinações.

- Warnings do fitparse (biblioteca externa) durante pytest:
  "datetime.utcfromtimestamp() is deprecated". São 3611 warnings em
  tests/test_calories.py. Não quebram, mas poluem a saída. Se um dia
  atualizar fitparse, somem. Baixa prioridade.

- Web: miniatura do feed usa 1 tile OSM centralizado (bbox grande pode cortar
  bordas). Aceitável; se virar problema, evoluir para mosaico 2x2 ou
  staticmap.openstreetmap.de.

- Mobile: sem inclinação/rotação 3D (flutter_map é 2D). Se 3D for requisito,
  avaliar maplibre_gl (decisão maior, pesada).

- TimeoutException do app mobile não reproduzido desde a Sessão 9. Registrar
  se voltar (tela + log do flutter run).

- (Oportunidade) RouteMap.tsx foi extraído na Sessão 13. Agora é reutilizável
  em qualquer página que precise renderizar uma rota. Se aparecer um segundo
  uso, considerar React.lazy() para tirar o leaflet (163 kB) do chunk da
  página que não mostra mapa.

- Stats no perfil: /activities/stats/summary, /weekly e /monthly são só do
  current_user. Se um dia o requisito for "ver stats de outro usuário",
  precisa de novos endpoints (com privacidade, provavelmente via follow).

===============================================================================
8. PRÓXIMOS PASSOS RECOMENDADOS (Sessão 14)
===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 14 (antes de qualquer mudança de código):
  1) Colar este handoff em docs/HANDOFF.md e commitar como
     `docs: handoff da Sessão 13`.
  2) No terminal (PowerShell via Win+R → "powershell"):
        cd D:\Rumo
        git push
        git log --oneline -5
        git status --short
        cd web ; npm run build
        cd ..\mobile
        & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
     Confirmar com o usuário: push aceito, HEAD == origin/main, build e
     analyze verdes, working tree limpo.
  3) DOCKER + PYTEST LOCAL:
        docker version
        docker compose version
        cd D:\Rumo\backend
        docker compose -f docker-compose.test.yml up -d
        docker ps
        .\.venv\Scripts\Activate.ps1
        pytest -q
     Esperado: 111 passed.
  4) DESCOBERTA DE ESTRUTURA (obrigatória — não adivinhar):
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

ORDEM DE TRABALHO RECOMENDADA (uma das duas rotas):

ROTA A — Refatorar os 4 gráficos em 1 `<PeriodChart>` (dívida recém-criada)
  Escopo médio, frontend. Reduzir duplicação antes que ela vire raiz.
  Passos:
    a) Ler os 4 arquivos atuais (WeeklyChart, MonthlyChart,
       WeeklyActivitiesChart, MonthlyActivitiesChart).
    b) Propor `components/PeriodChart.tsx` com props:
         period: "weekly" | "monthly"
         metric: "distance" | "activities"
         items, isLoading, isError
       Encapsula: label do eixo X (DD/MM vs MM/YYYY), título, tooltip,
       conversão km (só metric="distance"), yMax dinâmico (contagem) e
       allowDecimals (só activities).
    c) Entregar PeriodChart.tsx completo.
    d) Entregar ProfilePage.tsx usando `<PeriodChart ... />` em vez dos 4
       componentes (as 4 combinações viram 1 chamada parametrizada).
    e) Remover os 4 arquivos antigos (com confirmação explícita do usuário).
    f) npm run build + validação visual das 4 combinações em produção.
  Commit sugerido: `refactor(web): unifica gráficos do perfil em PeriodChart`.

ROTA B — Feature nova de backend (requer escolha com o usuário)
  Escopo médio-grande. Exemplos:
    - Drill-down de stats por tipo de atividade no perfil (tabela com
      uma linha por tipo, colunas: atividades, distância, tempo).
      Backend: 1 novo endpoint `/activities/stats/by-type`.
    - Comparação "este período vs. anterior" em cada gráfico.
    - Stats públicas para perfis de terceiros (com privacidade via follow).
  Requer: desenhar endpoint + schema + teste (agora VALIDÁVEL localmente,
  com pytest verde). Depois, UI no front.

  Rota A é a MINHA RECOMENDAÇÃO. O refactor é pequeno, fecha uma dívida
  criada agora, e mantém o ritmo de "deixar o repo melhor do que estava".
  A Rota B adiciona features, mas as dívidas acumulariam. Se o usuário
  preferir feature nova, Rota B é viável — mas o assistente deve explicitar
  que está adiando a dívida dos gráficos.

  Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes do
  fim, parar e entregar o HANDOFF completo da Sessão 14 neste mesmo formato
  (seções 0 a 8).