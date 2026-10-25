# HANDOFF — Rumo (backend + frontend + infra)

Data de encerramento: 2026-10-25 (sessão 3 — testes automatizados)
Duração da sessão: média — infra de testes + bloco de calorias coberto + debug de event loop
Próximo bloco recomendado: cobertura incremental (stats e social) OU Flutter mínimo.

## Resumo da sessão

Bloco de testes automatizados entregue:

- Infra: pytest + pytest-asyncio + httpx + Postgres 16 + PostGIS em Docker
  (docker-compose.test.yml, porta 5433, banco rumo_test).
- 21 testes passando: _estimate_calories (unit), _get_user_weight_kg (unit
  com banco), upload GPX/FIT (integração via rota real).
- Banco de teste isolado do Neon de prod; NullPool no engine de teste.

Calorias fechadas de ponta a ponta (sessões anteriores + esta):

- Backend calcula (MET × peso × horas) — validado em prod (GPX → 248, FIT → 350).
- UI aceita .fit no upload (commit 21957cf).
- UI exibe kcal no detalhe e no resumo de stats (commit 253e6bb).
- Testes congelam o comportamento (21 passando).

## Produção

- Backend: https://rumo-api-5s0b.onrender.com
- Docs: https://rumo-api-5s0b.onrender.com/docs
- Frontend: https://rumo-wheat.vercel.app
- Repo local: D:\Rumo

## Commits no main (origin/main = HEAD)

- (próximo commit) — test: infra de testes + cobertura do bloco de calorias (21 testes)
- 253e6bb — feat: exibe calorias no detalhe da atividade e no resumo de stats
- 21957cf — feat: aceita .fit no upload (UI) e mensagem de erro .gpx/.fit
- eb92676 — chore: remove log sentinela do calculo de calorias apos validacao em prod
- e6899f5 — debug: log sentinela (histórico, removido em eb92676)
- c51ee2c — docs: atualiza HANDOFF
- 340dfd9 — feat: estimativa de calorias no upload (MET x peso x duracao)

## Estado do código (backend)

### activity_service.py — completo

- _MET_BY_TYPE (run=9.8, walk=3.5, cycle=7.5, hike=6.0, swim=8.0, other=5.0)
- _MET_DEFAULT=5.0, _DEFAULT_WEIGHT_KG=70.0
- _estimate_calories(activity_type, duration_s, weight_kg) -> int | None:
  * None se duração ausente/zero/negativa
  * peso <= 0 ou None → fallback _DEFAULT_WEIGHT_KG
  * tipo desconhecido ou None → _MET_DEFAULT
  * retorno: max(0, int(round(kcal))) — clamp protege contra MET corrompido
- _get_user_weight_kg(db, user_id) -> float — 1 query, Decimal→float, fallback 70
- create_activity, create_activity_from_gpx, create_activity_from_fit —
  todos calculam se calories is None

### models

- User.weight_kg: Numeric(5, 2), nullable
- Activity.calories: Integer, nullable, CheckConstraint >= 0
- Activity.route: Geometry(LINESTRING, 4326) — PostGIS obrigatório em teste

## Estado do código (frontend) — inalterado nesta sessão

- UploadPage.tsx — aceita .gpx e .fit
- format.ts — formatCalories(kcal) com toLocaleString pt-BR
- ActivityDetailPage.tsx — grade de 5 métricas (Distância, Duração, Pace, Elevação, Calorias)
- StatsCards.tsx — 5 cards (Atividades, Distância, Tempo, Elevação, Calorias)
- ActivityCard.tsx — NÃO exibe calorias (decisão mantida)

## Infraestrutura de testes (NOVO)

### Arquivos

- backend/pytest.ini — asyncio_mode=auto, asyncio_default_fixture_loop_scope=session
- backend/docker-compose.test.yml — Postgres 16 + PostGIS, porta 5433, tmpfs
- backend/tests/__init__.py — pacote
- backend/tests/conftest.py — fixtures: test_engine (NullPool), db_session, test_user, client
- backend/tests/test_calories.py — 21 testes
- backend/samples/sample_run.fit — FIT sintético do Garmin SDK (versionado)
- backend/requirements.txt — pytest-cov adicionado

### Como rodar

```powershell
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml ps  # espera healthy
pytest -v

Decisões de design dos testes

    Banco: Postgres 16 + PostGIS em Docker, porque Activity.route é
    Geometry(LINESTRING, 4326). SQLite não serve.

    NullPool no test_engine: elimina "attached to a different loop" entre
    testes no Windows. Sem ele, asyncpg mantém conexões presas ao loop antigo.

    client não depende de db_session: abre sessão nova por request.
    Compartilhar a sessão do teste com a request HTTP causava
    "another operation is in progress".

    loop_scope="session" nos testes de _get_user_weight_kg: força o
    teste a rodar no mesmo loop da fixture. asyncio_default_test_loop_scope
    NÃO existe no pytest-asyncio 0.25 — usar marker explícito.

    TRUNCATE ... CASCADE por teste: create_all/drop_all uma vez por
    sessão (rápido), estado limpo entre testes via TRUNCATE.

    get_current_user sobrescrito: testes não exercitam JWT.

Pendências imediatas

Nenhuma bloqueante.
Próximo bloco recomendado

Duas opções, em ordem de preferência:
Opção A (recomendada) — cobertura incremental de testes

Adicionar testes para:

    stats_service: get_summary, get_period_stats (semana/mês)

    follow_service / like_service / comment_service: caminho felizes + 403/404

    auth: registro + login + token inválido

Por quê: consolidar a base de testes antes de abrir frente nova. Cada bloco
futuro (Flutter, diferenciais Strava) ganha rede de segurança.
Opção B — Bloco 14a: Mobile Flutter mínimo

App Flutter que consome a API (login, feed, detalhe). Frente nova, mais pesada.

Recomendação: A primeiro. Frente nova só depois de consolidar.
Dívidas conhecidas (atualizadas)
Backend

    FIT_SPORT_MAP pode estar incompleto para firmwares específicos

    Upload de foto síncrono

    Delete de foto no Cloudinary silencia exceção

    GET /activities/{id} aceita dono OU seguidor (is_public em aberto)

    ~~Sem testes automatizados~~ ← RESOLVIDO (calorias coberta; resto ainda sem)

    UserResponse expõe email/birth_date

    GET /activities/{id}/comments exige auth

    Upload GPX/FIT síncrono

    Cold start do Render free tier

    Stats só do current_user

    Sem índice pg_trgm para busca

    Inconsistência 403 (escrita) vs 404 (leitura social)

    parse_fit NÃO extrai total_calories do FIT — sempre cai no _estimate_calories

    fitparse gera 3610 DeprecationWarning (datetime.utcfromtimestamp) —
    biblioteca externa, não bloqueia, resolver quando atualizar fitparse

Frontend

    Contagem de likes no card é local

    Mapa sem layer switcher

    Tipos não gerados do OpenAPI

    react-hooks/set-state-in-effect desabilitada no ESLint

    Sem tratamento global de 401 pós-login

    client.ts: as string no VITE_API_URL

    ActivityCard fallback "Atividade" genérico

    Upload sem rascunho / AbortController

    SearchPage replace: true

Infra

    Docker Desktop precisa estar aberto (inclusive para testes)

    .env local aponta para Neon (prod) ou Docker

    Cloudinary free tier: 25 créditos/mês

    vercel.json em web/

    .vscode/settings.json ignorado — não versionar

    Render pode ficar com deploy velho mesmo mostrando "Your service is live".
    Sintoma: comportamento de código antigo. Solução: novo push/redeploy manual.

Armadilhas conhecidas (atualizadas)
Testes / pytest-asyncio

    asyncio_default_test_loop_scope NÃO existe no pytest-asyncio 0.25.0
    — usar @pytest.mark.asyncio(loop_scope="session") no teste.

    NullPool é obrigatório no engine de teste asyncpg no Windows. Sem ele,
    asyncpg mantém conexões presas ao loop antigo e estoura
    "attached to a different loop" entre testes.

    client fixture não pode reutilizar db_session: compartilhar a conexão
    do teste com a request HTTP causa "another operation is in progress".
    Abrir sessão nova por request via test_engine.

    TRUNCATE TABLE <lista> sem IF EXISTS — se a lista de tabelas do
    conftest.py divergir dos __tablename__ reais, quebra. Manter em sincronia
    ao adicionar tabela nova.

    os.environ["DATABASE_URL"] = ... (não setdefault) — pydantic-settings
    carrega .env e pode sobrescrever.

Backend / Python

    bcrypt==4.0.1 obrigatório

    greenlet==3.1.1 explícito

    uuid.uuid7 não existe — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso

    selectinload obrigatório em async

    Asyncpg + Numeric devolve Decimal — float() antes de multiplicar por MET

    alembic revision cria; alembic upgrade head aplica

    venv é D:\Rumo\backend.venv (com ponto)

    cloudinary.uploader.upload é síncrono

    Pydantic v2: str obrigatório rejeita null

    include_router COM prefix + router que já declara prefix = /prefix/prefix

    IntegrityError → rollback → depois notificação

    Rotas estáticas ANTES das dinâmicas

    slowapi exige request: Request na signature

    ServiceError não herda de HTTPException — try/except no router é obrigatório

    Renomear símbolo: Select-String pelo nome antigo antes de commitar

    fitparse: get_messages("record"), FitFile(BytesIO(...)) em try/except

    calories é Integer + CheckConstraint >= 0

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    WKT LINESTRING: ordem (lon lat)

    Neon: CREATE EXTENSION IF NOT EXISTS postgis;

    ILIKE %termo% NÃO usa B-tree

Render

    Free tier dorme após 15 min

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head &&

    requirements.txt PRECISA ir no commit

    Deploy Failed com ImportError: traceback mostra a linha

    Deploy pode ficar velho mesmo com "Your service is live". Forçar novo push.

Cloudinary

    Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

    secure_url é a URL HTTPS; public_id é para deletar

Vercel

    vercel.json em web/

    SPA fallback obrigatório

    Env vars VITE_* só client-side

Frontend / Vite 8 / React 19 / Tailwind 3

    Vite 8 usa Rolldown — build.manualChunks objeto quebrou TS

    erasableSyntaxOnly: true

    noUnusedLocals + noUnusedParameters ativos

    tailwindcss@3 fixo

    react-leaflet v5 + React 19: importar CSS no main.tsx

    MapContainer precisa height explícita

    <Polyline> espera [[lat, lng], ...]

    React Router v7: react-router-dom

    Backend espera form-urlencoded no login

    FormData no apiFetch: NÃO setar Content-Type

    <AuthProvider> no main.tsx

    Componentes = named export; páginas = default export
    <Link> dentro de <Link>: HTML inválido

    Recharts 3.x: react-is peerDependency

    <img> com object-cover + h-32 corta — usar aspect-square

    useInfiniteQuery: data.pages.flat() ?? []; initialPageParam obrigatório

    React.lazy exige export default

    ActivityCard recebe activity + author? (props separadas)

    Select-String -Recurse NÃO existe no PowerShell 5.1. Usar
    Get-ChildItem -Recurse -Include .ts,.tsx | Select-String -Pattern "..."

    toLocaleString("pt-BR") em número formata milhar com ponto

Ambiente / tooling

    .env e .env.local nunca commitados

    Docker Desktop precisa estar aberto

    docker compose down -v NUNCA

    curl no PowerShell é alias de Invoke-WebRequest — usar curl.exe

    Invoke-RestMethod com $variable no path: sempre interpolar

    Ordem de rotas: estáticas antes das dinâmicas

    npm sempre dentro de web/

    VS Code: python.defaultInterpreterPath → .venv/Scripts/python.exe (Windows)

    git status antes de commitar

    Token no localStorage: rumo.token

    Checklist de commit Python: ruff → python -c "from ... import ..." →
    Select-String símbolos → Select-String nome antigo → git add + commit + push

    Invoke-RestMethod com 204 vazio pode dar erro de parsing.
    Usar curl.exe -i para ver status real.

FIT

    fitparse.FitFile(BytesIO(bytes)), get_messages("record"), get_messages("session"),
    get_messages("file_id")

    Coordenadas em semicírculos: * (180.0 / 2**31)

    session.total_timer_time (pausa) vs total_elapsed_time (relógio) — usar
    total_timer_time

    record.distance acumulada em metros

    record.speed em m/s

    FIT de workout/course não tem record → rejeitar

    file_id.manufacturer = 'development' + serial = 1234 = sintético

    Indoor com GPS desligado: position_lat = 0 e position_long = 0 → filtrar

    parse_fit atual NÃO extrai total_calories — sempre cai no _estimate_calories

Usuários e IDs de teste

Prod (Neon):

    prod@rumo.com / senha12345 — username produser,
    id 01a12c83-be2a-71fa-b966-1c93ca64f341

    prod2@rumo.com / senha12345 — username Prod2,
    id 01a141e7-5ea4-7600-8959-19145475ad0a

    produser segue Prod2

Arquivos locais:

    D:\Activity.fit — sintético Garmin FIT SDK (94.096 bytes)

    D:\Caminhada_vespertina.gpx — GPX real

Samples no repo:

    backend/samples/sample_run.gpx — cópia do GPX real (277.147 bytes)

    backend/samples/sample_run.fit — cópia do FIT sintético (94.096 bytes)

Banco de teste (Docker):

    postgresql+asyncpg://rumo:rumo@localhost:5433/rumo_test

Primeira ação no próximo chat

    Confirmar que o commit do bloco de testes está no origin/main.

    Confirmar que Docker Desktop está aberto e o compose de teste está de pé
    (ou subir com docker compose -f docker-compose.test.yml up -d).

    Rodar pytest -v para confirmar 21/21 antes de qualquer alteração.

    Iniciar cobertura incremental: próximo alvo é stats_service (get_summary,
    get_period_stats) — testes similares aos de calorias, usando db_session
    e test_user.