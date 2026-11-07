===============================================================================
HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 15
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
  (118 passed ao fim da Sessão 15). Container de teste `rumo_postgres_test`
  na porta 5433. Para reativar numa sessão nova: (1) abrir Docker Desktop e
  esperar a baleia verde; (2) garantir que o terminal foi aberto via Win+R
  (fora do VS Code / Windows Terminal, que herdam PATH antigo); (3) `docker
  compose -f docker-compose.test.yml up -d`; (4) `pytest -q`.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)
--------------------------------------------------------------------
Árvore de alto nível REAL, confirmada no início da Sessão 15:

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
│   │   ├── services\   # activity_service.py, comment_service.py, errors.py,
│   │   │               # feed_service.py, fit_service.py, follow_service.py,
│   │   │               # gpx_service.py, like_service.py, notification_service.py,
│   │   │               # photo_service.py, stats_service.py, user_service.py
│   │   └── __pycache__\
│   ├── samples\
│   ├── scripts\
│   ├── tests\          # conftest.py + test_calories.py + test_comment.py +
│   │                   # test_follow.py + test_like.py + test_stats.py
│   ├── _scratch\
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
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
        │               # photos.ts, social.ts, stats.ts (getStatsByType)
        ├── assets\
        ├── components\ # ActivityCard, ActivityResults, AppHeader,
        │               # CommentsSection, LikeButton, NotificationBell,
        │               # PeriodChart (unifica 4 gráficos), PhotoGallery,
        │               # PhotoUpload, ProtectedRoute, RouteMap, StatsCards,
        │               # UserResults
        ├── contexts\
        ├── hooks\      # useActivities, useActivitySearch, useAuth, useDebounce,
        │               # useNotifications, usePhotos, useProfile, useSocial,
        │               # useStats (useStatsByType), useUserSearch
        ├── lib\        # format.ts (formatDistance/Duration/Pace/Speed/
        │               # Calories/DateTime/RelativeDate/ActivityType/Emoji +
        │               # formatElevation — S15), geo.ts
        ├── pages\      # ActivitiesPage, ActivityDetailPage, FeedPage,
        │               # LoginPage, NotificationsPage, ProfilePage,
        │               # RegisterPage, SearchPage, UploadPage
        └── types\      # api.ts (todos os tipos, StatsByType* — S14)

DIVERGÊNCIAS vs handoff da Sessão 14:
- `backend/` NÃO tem `pyproject.toml`. Gerenciador de deps é
  `requirements.txt` (fitparse removido, fitdecode>=0.11.0 no lugar — S15).
- `backend/app/services/` tem `fit_service.py` reescrito para `fitdecode`.
- `web/src/lib/format.ts` ganhou `formatElevation` (S15).
- `web/src/components/StatsCards.tsx` usa `formatElevation` (S15).

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
      7. `pytest -q` — esperado: **118 passed, 0 warnings** (verde ao fim da Sessão 15)
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
- ATENÇÃO — `git log` sem `--no-pager` abre o `less` e trava o terminal.
  SEMPRE usar `git --no-pager log ...` ou prefixar com `$env:PAGER=""`.

ACORDOS DE TRABALHO (válidos em todas as sessões)
--------------------------------------------------
1. SEMPRE seguir a recomendação do assistente. Quando houver decisão
   pendente, executar a recomendada salvo instrução explícita em contrário.
   (O usuário reforçou isso no início da Sessão 15.)
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

- Backend: 118 testes passando LOCALMENTE (pytest -q verde na Sessão 15),
  0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track
  devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat],
  bbox [minLon,minLat,maxLon,maxLat], n_points, simplified. Responde 404
  quando route é NULL.
- ActivityResponse (feed/lista/detalhe/busca) inclui
  `bbox: list[float] | None`, calculado via ST_XMin/YMin/XMax/YMax do PostGIS
  no mesmo SELECT (sem N+1). `None` quando route é NULL.
- Endpoints de stats (todos validados em produção):
  * GET /activities/stats/summary — StatsSummary (totais gerais).
  * GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.
  * GET /activities/stats/monthly?months=N — StatsMonthlyResponse.
  * GET /activities/stats/by-type — StatsByTypeResponse (S14).
  Os 3 primeiros aceitam `activity_type` opcional como filtro. O by-type
  NÃO aceita filtro (o objetivo é ver todos os tipos lado a lado).
- Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet
  (RouteMap no detalhe) + recharts (gráficos no perfil).
- Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
  alternância Mapa/Satélite, miniatura estática no feed. Sem mudanças na S15.
- [Sessão 15 — entregas]
  * Rota A(a) — silenciar warnings do fitparse: `pytest.ini` ganhou
    `filterwarnings = ignore::DeprecationWarning:fitparse\.processors`,
    apagando os 3611 warnings (2 únicos, deduplicados) do parsing de .FIT
    sem esconder warnings de outras libs. Commit fa4fcc4.
    (SUPERADA na própria S15: fitparse foi removido — ver abaixo.)
  * Rota A(b) — coluna "Pace médio" no drill-down por tipo: `ProfilePage.tsx`
    ganhou a coluna (entre Tempo e Calorias), com regra
    `PACE_TYPES = {run, walk, hike}` → `formatPace()`, senão `"—"`. O pace
    é calculado no front (`total_duration_s / (total_distance_m / 1000)`),
    com guarda para `total_distance_m <= 0`. De brinde, foram removidas as
    duas funções inline duplicadas (`formatDistance`, `formatDuration`) que
    existiam desde a S14 — agora vêm de `lib/format.ts`. Commit 053239c.
  * Rota A(c) — documentar a decisão dos enums nativos do Postgres: seção 7,
    "Armadilha conhecida". Commit d7d756e.
  * Rota A(a) — migração `fitparse` → `fitdecode` (a dívida real):
    - `app/services/fit_service.py` reescrito com `fitdecode.FitReader`
      (iteração por frames `FIT_FRAME_DATA`, `frame.get_value(...)` em vez de
      `FitFile.get_messages(...)`). Assinatura pública (`parse_fit`,
      `map_fit_sport`) e formato de retorno (`gpx_type`, `track_points` como
      `[[lat, lon, ele, unix_ts], ...]`) preservados.
    - CRC desabilitado (`check_crc=fitdecode.CrcCheck.DISABLED`) para manter
      a tolerância do fitparse a arquivos com CRC inválido.
    - `requirements.txt`: `fitparse>=1.2.0` → `fitdecode>=0.11.0`.
    - `pytest.ini`: filtro `filterwarnings` removido (não é mais necessário
      — os warnings desapareceram na origem).
    - `fitparse` desinstalado do venv. Nenhum `.py` do projeto importa mais.
    - Validação: 118 passed, 0 warnings (por ausência real, não por filtro).
    - Commit 3cf7668.
  * Rota A(b) — coluna "Elevação" no drill-down por tipo:
    - `lib/format.ts`: +`formatElevation` (metros sempre, nunca km; milhar
      pt-BR: "1.234 m"; null → "—").
    - `pages/ProfilePage.tsx`: coluna "Elevação" entre "Distância" e "Tempo".
    - `types/api.ts`: sem mudança (`total_elevation_gain_m` já existia desde
      a S14).
    - Commit fdac345.
  * Rota A(b-extra) — `StatsCards.tsx` usa `formatElevation` em vez de
    formatar inline. Alinha com `formatDistance`/`formatDuration`/
    `formatCalories`. 0 m agora mostra "0 m" (dado real) em vez de "—".
    Commit 4cfd099.
  * Estado final: working tree limpo, HEAD == origin/main == 4cfd099,
    pytest 118 passed / 0 warnings, npm run build verde (824 modules).

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
- Git (estado ao fim da Sessão 15):
    4cfd099  (HEAD -> main, origin/main) refactor(web): StatsCards usa formatElevation em vez de inline
    fdac345  feat(web): coluna de elevacao no drill-down por tipo
    3cf7668  refactor(backend): migra parsing de .FIT de fitparse para fitdecode
    d7d756e  docs: registra entregas da Sessao 15 (A-a, A-b) e decisao sobre enums
    053239c  feat(web): coluna de pace medio no drill-down por tipo
    fa4fcc4  test(backend): silencia deprecation do fitparse via filterwarnings no pytest.ini
- Todos os commits da Sessão 15 estão em origin/main (pushados).
- Render e Vercel deployam automático a cada push em main. Os endpoints
  /activities/stats/by-type e as colunas novas (Elevação, Pace médio) já
  estão no ar.

===============================================================================
3. O QUE FOI FEITO NA SESSÃO 15
===============================================================================

3.1 Validação de estado inicial (Sessão 15)
    - Push OK (origin/main em d7d756e).
    - Working tree limpo.
    - npm run build verde (824 modules, 2.14s).
    - flutter analyze: No issues found (3.3s).
    - docker version OK, compose v5.5.1 OK.
    - rumo_postgres_test Up healthy na 5433.
    - pytest -q: 118 passed, 0 warnings.
    - Descoberta de estrutura via Get-ChildItem — sem divergências vs handoff
      da Sessão 14, exceto por 2 arquivos lixo (`rc*` com caractere inválido)
      no working tree, removidos antes do primeiro commit.

3.2 [Backend] Rota A(a) — migração fitparse → fitdecode
    - Lido `app/services/fit_service.py` (parser atual).
    - `fit_service.py` reescrito com `fitdecode.FitReader`:
      * Iteração por frames `FIT_FRAME_DATA` com `frame.name` em
        {"record", "session"}.
      * `frame.get_value("timestamp")` já devolve `datetime` UTC aware
        (sem `utcfromtimestamp`).
      * `check_crc=fitdecode.CrcCheck.DISABLED` para manter tolerância
        do fitparse.
      * Demais campos (`position_lat/long`, `altitude`, `distance`,
        `total_timer_time`, `sport`) via `frame.get_value(...)`.
      * API pública e formato de retorno preservados.
    - `requirements.txt`: `fitparse>=1.2.0` → `fitdecode>=0.11.0`.
    - `pytest.ini`: bloco `filterwarnings` + comentário-dívida removidos.
    - `pip install fitdecode`, `pip uninstall fitparse`.
    - Validação: 118 passed, 0 warnings.
    - Commit: 3cf7668.

3.3 [Web] Rota A(b) — coluna "Elevação" no drill-down
    - `lib/format.ts`: +`formatElevation` (metros sempre, nunca km;
      milhar pt-BR).
    - `ProfilePage.tsx`: +coluna "Elevação" entre "Distância" e "Tempo";
      +import de `formatElevation`; +`<td>` com
      `formatElevation(item.total_elevation_gain_m)`.
    - `types/api.ts`: sem mudança (`total_elevation_gain_m` já existia).
    - npm run build: 824 modules (era 824), ProfilePage 14.40 kB.
    - Commit: fdac345.

3.4 [Web] Rota A(b-extra) — `StatsCards` usa `formatElevation`
    - `StatsCards.tsx`: formatação inline (`${Math.round(...)} m`) trocada
      por `formatElevation(data.total_elevation_gain_m)`.
    - Alinha com `formatDistance`/`formatDuration`/`formatCalories`.
    - 0 m agora mostra "0 m" (dado real) em vez de "—" (ausência).
    - npm run build: verde, 1.66s.
    - Commit: 4cfd099.

3.5 Estado final da sessão
    - Working tree limpo, main == origin/main == 4cfd099.
    - npm run build: verde (824 modules).
    - pytest -q: 118 passed, 0 warnings (local).
    - flutter analyze: No issues found.
    - Nenhuma pendência de git.

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

- GET /activities/stats/by-type  (S14 — sem query params)
  → StatsByTypeResponse:
    {
      "items": [
        {
          "activity_type": "run",  // string
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

- Sessões 9, 10, 11, 12, 13, 14 e 15 commitadas e pushadas.
- origin/main == main == HEAD == 4cfd099.
- Sessão 15 fechada com este handoff (commit `docs: handoff da Sessão 15`).
- Nenhuma pendência conhecida de git.

===============================================================================
6. SCRIPTS ÚTEIS (PowerShell)
===============================================================================

# [Sessão 16 — primeira ação] Abrir PowerShell via Win+R → "powershell"
# (NÃO abrir de dentro do VS Code / Windows Terminal)
# Depois:

# [Sessão 16 — primeira ação] Descoberta da estrutura do repo
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

# [Sessão 16 — primeira ação] Estado do repo (sem abrir o less)
cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

# [Sessão 16 — primeira ação] Sanidade de build
cd D:\Rumo\web
npm run build

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

# [Sessão 16 — primeira ação] Docker + pytest local
docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps
.\.venv\Scripts\Activate.ps1
pytest -q

# Verificar que fitdecode está instalado e fitparse NÃO
python -c "import fitdecode; print('fitdecode OK:', fitdecode.__version__)"
python -c "import fitparse" 2>&1   # esperado: ModuleNotFoundError

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

- (RESOLVIDA na Sessão 15) fitparse (biblioteca externa, última release
  1.2.0 em 2020, dormente) era a fonte de 3611 warnings
  `datetime.utcfromtimestamp() is deprecated` no pytest. RESOLUÇÃO:
  migração para `fitdecode` (ativo, mantido, sem `utcfromtimestamp`).
  `fit_service.py` reescrito, `requirements.txt` atualizado, `pytest.ini`
  sem filtro, fitparse desinstalado. Commit 3cf7668.

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
  do chunk da página que não mostra mapa. Ganho hoje é marginal.

- (Oportunidade) Drill-down de stats por tipo poderia ganhar, no futuro:
  * (RESOLVIDO na Sessão 15) Coluna "Pace médio". Commit 053239c.
  * (RESOLVIDO na Sessão 15) Coluna "Elevação". Commit fdac345.
  * Filtro por período (ex.: "últimos 90 dias"). Hoje mostra "todos os
    tempos" — o que é o que o usuário quer no drill-down, mas vale
    considerar se surgir demanda.

- (Oportunidade) Stats no perfil: /activities/stats/summary, /weekly,
  /monthly e /by-type são só do current_user. Se um dia o requisito for
  "ver stats de outro usuário", precisa de novos endpoints (com
  privacidade, provavelmente via follow).

===============================================================================
8. PRÓXIMOS PASSOS RECOMENDADOS (Sessão 16 e além)
===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 16 (antes de qualquer mudança de código):
  1) No terminal (PowerShell via Win+R → "powershell"):
        cd D:\Rumo
        git push
        git --no-pager log --oneline -8
        git status --short
        cd web ; npm run build
        cd ..\mobile
        & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
     Confirmar com o usuário: push aceito, HEAD == origin/main == 4cfd099
     (ou o commit do handoff), build e analyze verdes, working tree limpo.
  2) DOCKER + PYTEST LOCAL:
        docker version
        docker compose version
        cd D:\Rumo\backend
        docker compose -f docker-compose.test.yml up -d
        docker ps
        .\.venv\Scripts\Activate.ps1
        pytest -q
     Esperado: 118 passed, 0 warnings.
  3) Verificar que a migração do fitdecode está ativa:
        python -c "import fitdecode; print('fitdecode OK:', fitdecode.__version__)"
        python -c "import fitparse" 2>&1   # esperado: ModuleNotFoundError
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

ESTADO DA ROTA A+ (Sessão 15): FECHADA.
  (a) migração fitparse → fitdecode → FEITO (3cf7668).
  (b) coluna "Elevação" → FEITO (fdac345).
  (b-extra) StatsCards usa formatElevation → FEITO (4cfd099).
  (c) decisão dos enums documentada → FEITO (d7d756e).

ROTA A+ — Sugestões de continuação para a Sessão 16 (baixo risco):
  a) Miniatura do feed: evoluir de 1 tile OSM para mosaico 2×2 ou usar
     staticmap.openstreetmap.de. Requer ler `RouteMap`/`ActivityCard` do
     web e o widget equivalente do mobile. Ganho visual; custo médio.
  b) RouteMap com React.lazy() — prepara o terreno para segundo uso do
     mapa (hoje só ActivityDetailPage usa). Ganho marginal hoje.
  c) Cheat sheet de endpoints no HANDOFF ou num futuro README
     (seção 4 já cobre, mas é verbosa).

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

  A recomendação para a Sessão 16 é começar pela ROTA A+ (a) — miniatura
  do feed —, que é a dívida visual mais concreta e de escopo bem delimitado.
  Se o usuário preferir feature nova, Rota B é viável — mas o assistente
  deve explicitar que está adiando dívidas.

  Em qualquer rota, handoff preventivo em ~70-80% do contexto — antes do
  fim, parar e entregar o HANDOFF completo da Sessão 16 neste mesmo formato
  (seções 0 a 8).