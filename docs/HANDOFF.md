# Rumo — Handoff Atualizado (após Bloco 13a.3)

## Sobre o projeto
Sistema de monitoramento de exercícios físicos (tipo Strava). Nome: **Rumo**.
Usuário: iniciante em Python/backend, experiente em JS (2 sistemas em produção).
Objetivo: produção real, com usuários reais usando no dia a dia.

---

## Visão do produto (NORTE — ler antes de qualquer decisão)

**O Rumo é um app de exercício físico ambicioso, semelhante ao Strava.** Não é
um projeto de portfólio nem um CRUD de treinos. O objetivo é produção real,
com usuários reais usando no dia a dia.

### O que o Rumo DEVE ter (roadmap ambicioso)

**Core (essencial pra ser "Strava-like"):**
- [x] Auth (register/login/JWT)
- [x] CRUD de atividades
- [x] Upload de GPX com cálculo automático (distância, pace, elevação)
- [ ] Upload de FIT (formato cru dos relógios Garmin/Polar)
- [ ] Upload de fotos da atividade (storage S3/Cloudinary/R2)
- [ ] Perfil público com stats agregadas (km totais, PRs, gráficos)
- [ ] Splits por km (pace e elevação por trecho)
- [ ] Mapa/visualização da rota no cliente (endpoint dedicado) ← **13a.4**

**Social (o que faz o app engajar):**
- [x] Follows (seguir/seguidores)
- [x] Feed (atividades próprias + de quem segue)
- [x] Likes (kudos)
- [x] Comentários
- [ ] Notificações push ("fulano curtiu", "sicrano te seguiu", "novo PR")
- [ ] Feed personalizado com filtros (só corrida, só amigos mútuos)
- [ ] Compartilhamento externo (card/imagem pra Instagram/WhatsApp)

**Diferenciais (o que faz o Strava ser Strava):**
- [ ] Segments (trechos famosos onde compete por tempo contra outros)
- [ ] Leaderboards por segmento
- [ ] Achievements/badges ("primeiro 10K", "recorde pessoal")
- [ ] Análise de treino (zonas de FC, cadência, comparação semana a semana)

**Infra/operacional (obrigatório antes de ir pra produção real):**
- [ ] Rate limiting
- [ ] Cache (Redis — já no docker-compose, não usado ainda)
- [ ] Testes automatizados
- [ ] Background jobs (processar GPX grandes fora do request)
- [ ] Observabilidade (logs estruturados, métricas, tracing)
- [ ] Backup do banco

### Como usar essa visão

Quando estiver em dúvida sobre uma decisão técnica, **perguntar: isso aproxima
o Rumo do Strava ou afasta?** Exemplos:

- "Devo expor `raw_track_points` no `ActivityResponse`?" → **Não**, porque
  o cliente (mobile) vai precisar desenhar o mapa — melhor endpoint dedicado
  que retorna só a geometria, pra não pesar a listagem.
- "Devo fazer upload GPX síncrono ou em background?" → No MVP síncrono;
  no futuro, background com fila (Celery/RQ/arq) pra aguentar arquivos grandes.
- "Devo usar SQLite pra simplificar?" → **Não.** PostGIS é obrigatório (Strava
  é geo-first). Neon já está planejado.

### O que o Rumo NÃO é

- ❌ Não é um projeto de portfólio — é um produto de verdade.
- ❌ Não é um "CRUD de exercícios" — é uma rede social de exercícios.
- ❌ Não é um clone literal do Strava — é inspirado, com identidade própria.

---

## Roadmap em fases (vertical slice, não horizontal)

**Estratégia:** construir features completas atravessando backend + frontend +
mobile, em vez de terminar o backend inteiro antes de começar o frontend.

**Por quê:**
1. "Backend 100%" é miragem — sempre falta algo.
2. Frontend/mobile **informam** o backend sobre o que ainda falta.
3. Ver funcionando na tela **recarrega a motivação**.
4. Deploy cedo é barato depois da primeira vez (Render faz redeploy automático).
5. Padrão da indústria é vertical slice, não horizontal.

### Fase 1 — Deploy + primeira feature visível (curto prazo)
1. ✅ **Bloco 11: Deploy backend** (Render + Neon) — **CONCLUÍDO**
2. ⏳ **Bloco 13a: Frontend mínimo** (React/Vercel)
   - ✅ **13a.0:** Setup Vite + TS + Tailwind + Router + Query + Leaflet
   - ✅ **13a.1:** Auth (login, registro, ProtectedRoute, AuthContext)
   - ✅ **13a.2:** Lista de atividades (cards, formatadores, empty state)
   - ✅ **13a.3:** Upload GPX (drag & drop + multipart + useMutation)
   - ⏳ **13a.4:** Detalhe + mapa (precisa de `GET /activities/{id}/track` no backend) ← PRÓXIMO
   - ⏳ **13a.5:** Deploy Vercel + CORS produção
3. ⏳ **Bloco 14a: Mobile mínimo** (Flutter) — mesma coisa

**Resultado:** app funcional de ponta a ponta. Sobe GPX, vê rota no mapa,
lista atividades. Suficiente pra usar de verdade e descobrir o que falta.

### Fase 2 — Refinar o que existe (médio prazo)
4. **Bloco 13b/14b:** feed, likes, comentários no frontend/mobile
5. **Bloco 15:** fotos de atividade
6. **Bloco 16:** perfil público + stats visuais

### Fase 3 — Diferenciais do Strava (longo prazo)
7. **Bloco 17+:** segments, achievements, notificações, análise de treino

**O que NÃO fazer:** tentar "terminar o backend antes de tudo". Isso atrasa
meses, mata a motivação, e ignora que o frontend ensina o backend.

---

## Stack

### Backend
- **Python:** 3.13.7 + FastAPI + SQLAlchemy 2.0 async + Alembic + GeoAlchemy2
- **Banco dev:** PostgreSQL 16.4 + PostGIS 3.4 (Docker, `postgis/postgis:16-3.4`)
- **Banco prod:** Neon (PostGIS habilitado, projeto `rumo`, branch `production`, região AWS US East 2 Ohio, PG **17.11** + PostGIS **3.5**)
- **Cache:** Redis (Docker, ainda não usado)
- **Deploy:** Render (Blueprint via `render.yaml`, free tier)
  - **URL produção:** `https://rumo-api-5s0b.onrender.com`
  - **Docs:** `https://rumo-api-5s0b.onrender.com/docs`

### Frontend (novo)
- **Vite 8.3.4** + **React 19.2.8** + **TypeScript 6.0.2**
- **React Router DOM 7.18.4** (modo SPA, `BrowserRouter`)
- **TanStack Query 5.104.2** (cache/servidor state)
- **react-hook-form 7.90.0** + **zod 4.6.6** + **@hookform/resolvers 5.9.1** (formulários)
- **Tailwind CSS 3.4.19** (paleta `rumo` custom + Inter)
- **Leaflet 1.9.4** + **react-leaflet 5.0.0** (mapas)
- **ESLint 10** (config flat do Vite v9, regra `react-hooks/set-state-in-effect` desabilitada — ver dívida técnica)
- **Deploy:** Vercel (ainda NÃO configurado — Bloco 13a.5)
- **Pasta:** `web/` na raiz do monorepo

### Repo / IDE / OS
- **Repo:** https://github.com/mmnc12/rumo (privado)
- **IDE:** VS Code (terminal integrado)
- **OS:** Windows (PowerShell)
- **Pacote:** npm

## Estrutura de pastas (atualizada)

D:\Rumo
├── .gitignore, README.md, docker-compose.yml, render.yaml
├── docs\HANDOFF.md
├── backend
│ ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│ ├── _scratch\ (NÃO versionado)
│ ├── samples\ (não versionado — GPX de teste)
│ ├── alembic\env.py + versions
│ │ └── 19cd7d2f4c3f_full_name_nullable_em_users.py
│ ├── app
│ │ ├── main.py, config.py, database.py
│ │ ├── core\security.py, core\dependencies.py
│ │ ├── models{user,activity,follow,like,comment,init}.py
│ │ ├── schemas{user,activity,stats,like,comment,init}.py
│ │ ├── routers{auth,activities,feed,users,comments,init}.py
│ │ └── services{activity_service,gpx_service,stats_service,follow_service,like_service,feed_service,comment_service,errors,init}.py
│ └── tests
├── mobile\ (vazio)
└── web
├── .env.local (não versionado), .env.example
├── .gitignore, eslint.config.js, index.html
├── package.json, package-lock.json, postcss.config.js
├── tailwind.config.js (paleta rumo)
├── tsconfig.json, tsconfig.app.json, tsconfig.node.json
├── vite.config.ts
└── src
├── api
│ ├── client.ts ← apiFetch + ApiError + token helpers
│ ├── auth.ts ← login/register/getMe
│ └── activities.ts ← list/get/delete/uploadGpx (13a.3)
├── components
│ ├── ProtectedRoute.tsx ← named export (13a.1)
│ ├── AppHeader.tsx ← named export + link "+ Enviar" (13a.3)
│ └── ActivityCard.tsx ← (13a.2)
├── contexts
│ └── AuthContext.tsx ← AuthProvider (named export)
├── hooks
│ ├── useAuth.ts
│ └── useActivities.ts ← queries + useUploadGpx (13a.3)
├── lib
│ └── format.ts
├── pages
│ ├── LoginPage.tsx ← default export
│ ├── RegisterPage.tsx ← default export
│ ├── ActivitiesPage.tsx ← default export
│ └── UploadPage.tsx ← default export (13a.3)
├── types
│ └── api.ts ← espelho dos schemas Pydantic
├── App.tsx ← rotas
├── main.tsx ← QueryClient + BrowserRouter + AuthProvider
└── index.css


## Models existentes (backend)

### User
- id (UUID v7), email (unique), username (unique), full_name (**nullable desde 13a.1**)
- hashed_password, weight_kg, height_cm, birth_date
- is_active, created_at, updated_at (todos `DateTime(timezone=True)`)

### Activity
- id (UUID v7), user_id (FK users CASCADE)
- activity_type (enum: run/walk/cycle/hike/swim/other)
- title, description
- started_at (indexed), finished_at, duration_s
- distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps
- route (Geometry LINESTRING 4326), raw_track_points (JSONB) — formato `[[lat, lon, ele, unix_ts], ...]`
- created_at, updated_at
- `user = relationship("User", backref="activities", lazy="raise")`

### Follow / Like / Comment
(inalterados desde o Bloco 10)

## Endpoints existentes (backend)

### Auth & Users
- `GET /` — metadados
- `GET /health` — status API + banco
- `POST /auth/register` — cria usuário (201, 409 se duplicado)
- `POST /auth/login` — form-urlencoded (username=email), retorna JWT
- `GET /auth/me` — protegido
- `POST /users/{user_id}/follow` — 204
- `DELETE /users/{user_id}/follow` — 204
- `GET /users/{user_id}/followers?limit&offset`
- `GET /users/{user_id}/following?limit&offset`

### Activities
- `POST /activities` — 201 (JSON pré-calculado)
- `POST /activities/upload` — 201 (multipart, `.gpx`)
- `GET /activities?limit=20&offset=0` — lista próprias
- `GET /activities/{id}` — detalhes (só do dono)
- `DELETE /activities/{id}` — 204
- `GET /activities/stats/summary?activity_type=`
- `GET /activities/stats/weekly?weeks=8&activity_type=`
- `GET /activities/stats/monthly?months=6&activity_type=`
- `POST /activities/{id}/like` — 200
- `DELETE /activities/{id}/like` — 204
- `GET /activities/{id}/likes?limit&offset` — 200

**⚠️ Endpoint a CRIAR no 13a.4:** `GET /activities/{id}/track` — retorna GeoJSON:
```json
{
  "activity_id": "uuid",
  "type": "LineString",
  "coordinates": [[lon, lat, ele], ...],
  "bbox": [minLon, minLat, maxLon, maxLat],
  "n_points": 2345,
  "simplified": false
}


## Models existentes (backend)

### User
- id (UUID v7), email (unique), username (unique), full_name (**nullable desde 13a.1**)
- hashed_password, weight_kg, height_cm, birth_date
- is_active, created_at, updated_at (todos `DateTime(timezone=True)`)

### Activity
- id (UUID v7), user_id (FK users CASCADE)
- activity_type (enum: run/walk/cycle/hike/swim/other)
- title, description
- started_at (indexed), finished_at, duration_s
- distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps
- route (Geometry LINESTRING 4326), raw_track_points (JSONB) — formato `[[lat, lon, ele, unix_ts], ...]`
- created_at, updated_at
- `user = relationship("User", backref="activities", lazy="raise")`

### Follow / Like / Comment
(inalterados desde o Bloco 10)

## Endpoints existentes (backend)

### Auth & Users
- `GET /` — metadados
- `GET /health` — status API + banco
- `POST /auth/register` — cria usuário (201, 409 se duplicado)
- `POST /auth/login` — form-urlencoded (username=email), retorna JWT
- `GET /auth/me` — protegido
- `POST /users/{user_id}/follow` — 204
- `DELETE /users/{user_id}/follow` — 204
- `GET /users/{user_id}/followers?limit&offset`
- `GET /users/{user_id}/following?limit&offset`

### Activities
- `POST /activities` — 201 (JSON pré-calculado)
- `POST /activities/upload` — 201 (multipart, `.gpx`)
- `GET /activities?limit=20&offset=0` — lista próprias
- `GET /activities/{id}` — detalhes (só do dono)
- `DELETE /activities/{id}` — 204
- `GET /activities/stats/summary?activity_type=`
- `GET /activities/stats/weekly?weeks=8&activity_type=`
- `GET /activities/stats/monthly?months=6&activity_type=`
- `POST /activities/{id}/like` — 200
- `DELETE /activities/{id}/like` — 204
- `GET /activities/{id}/likes?limit&offset` — 200

**⚠️ Endpoint a CRIAR no 13a.4:** `GET /activities/{id}/track` — retorna GeoJSON:
```json
{
  "activity_id": "uuid",
  "type": "LineString",
  "coordinates": [[lon, lat, ele], ...],
  "bbox": [minLon, minLat, maxLon, maxLat],
  "n_points": 2345,
  "simplified": false
}

Decisão tomada no 13a.0: não expor route/raw_track_points no ActivityResponse. Endpoint dedicado, só geometria, pra não pesar a listagem.
Comments

    POST /activities/{activity_id}/comments — 201

    GET /activities/{activity_id}/comments?limit&offset — 200

    DELETE /comments/{comment_id} — 204

Feed

    GET /feed?limit=20&offset=0

Frontend — Padrões e decisões (Bloco 13a)
web/ como monorepo

    Vercel vai apontar pra web/ (Root Directory). Render continua em backend/.

    .env.local NUNCA versionado.

Cliente HTTP (src/api/client.ts)

    apiFetch<T>(path, options) — única porta pro backend.

    Injeta JWT do localStorage (rumo.token) automaticamente.

    body (objeto) → JSON. rawBody (FormData/URLSearchParams) → passa cru.

    FormData NÃO deve setar Content-Type manualmente (o browser põe com boundary).

    401 limpa token automaticamente (força novo login).

    Erros viram ApiError(status, detail) — detail é o detail cru do FastAPI.

Auth (AuthContext + useAuth + ProtectedRoute)

    Token em localStorage; user em memória.

    Boot do app chama GET /auth/me se houver token (reidrata sessão).

    register() faz login automático depois do cadastro.

    ProtectedRoute redireciona pra /login guardando state.from.

    <AuthProvider> PRECISA envolver <App> no main.tsx — erro runtime se faltar.

Rotas atuais (App.tsx)

    /login, /register (públicas)

    /activities (protegida)

    /upload (protegida) ← 13a.3

    / → redireciona pra /activities

    * → 404 simples

Convenção de exports (IMPORTANTE — não misturar)

    Componentes reutilizáveis → named export (export function X)

        AppHeader, ProtectedRoute, ActivityCard

    Páginas → default export (export default function X)

        ActivitiesPage, UploadPage, LoginPage, RegisterPage

    Isso já custou um bug de build no 13a.3 (ProtectedRoute importado como default). Padrão confirmado — não misturar.

Upload GPX (13a.3)

    uploadGpx(file, meta?) em api/activities.ts usa rawBody: FormData.

    useUploadGpx() em hooks/useActivities.ts → useMutation invalidando activitiesKeys.all.

    UploadPage.tsx: drag & drop + validação client-side (.gpx, ≤20MB) + spinner + erro via ApiError.detail.

    Redireciona pra /activities no sucesso (o detalhe só existe no 13a.4).

    Link "+ Enviar" no AppHeader aponta pra /upload.

Formatadores (src/lib/format.ts)

    formatDistance(m), formatDuration(s), formatPace(sPerKm), formatSpeed(mps), formatDateTime(iso), formatRelativeDate(iso), formatActivityType("run"), activityEmoji("run")

TanStack Query (useActivities)

    Query keys: ["activities"], ["activities","list",params], ["activities","detail",id]

    staleTime: 30_000, retry 1, refetchOnWindowFocus: false

Tailwind

    Paleta custom: rumo-50 … rumo-900 (laranja). Primária: rumo-500 = #f97316.

    Fonte: Inter. Body: bg-gray-50 text-gray-900 antialiased.

Produção (Render + Neon)

    API: https://rumo-api-5s0b.onrender.com

    Deploy: git push origin main → Render rebuilda → alembic upgrade head → gunicorn (2 workers uvicorn).

    Free tier dorme após 15 min. Primeira request ~30-50s.

    Env vars no Render: DATABASE_URL, ENVIRONMENT=production, DEBUG=false, SECRET_KEY, ALGORITHM=HS256, ACCESS_TOKEN_EXPIRE_MINUTES=30, ALLOWED_ORIGINS=["http://localhost:5173"], PYTHON_VERSION=3.13.7

Blocos concluídos

    ✅ 1 a 9 (ver histórico)

    ✅ 10a Follows / 10b Feed / 10c Likes / 10d Comentários

    ✅ 12 Upload GPX backend

    ✅ 11 Deploy Render + Neon

    ✅ 13a.0 Setup Vite+TS+Tailwind+Router+Query+Leaflet

    ✅ 13a.1 Auth (login/registro/ProtectedRoute/AuthContext) + fix full_name nullable

    ✅ 13a.2 Lista de atividades (cards, formatadores, empty state)

    ✅ 13a.3 Upload GPX no frontend (drag & drop + useMutation + AppHeader "+ Enviar")

Blocos pendentes

    ⏳ 13a.4 Detalhe + mapa ← PRÓXIMO

        Backend primeiro:

            Schema TrackResponse em schemas/activity.py

            get_activity_track() em services/activity_service.py (lê route PostGIS → GeoJSON)

            GET /activities/{id}/track no router (protegido, só do dono)

        Frontend depois:

            getActivityTrack(id) em api/activities.ts

            useActivityTrack(id) em hooks/useActivities.ts

            ActivityDetailPage.tsx com <MapContainer> + <Polyline> (Leaflet)

            Rota /activities/:id no App.tsx

            ActivityCard vira <Link> pro detalhe

    ⏳ 13a.5 Deploy Vercel + CORS produção

        Vercel Root Directory = web/

        VITE_API_URL=https://rumo-api-5s0b.onrender.com nas env vars do Vercel

        Atualizar ALLOWED_ORIGINS no Render com URL real da Vercel

    ⏳ 14a Mobile Flutter mínimo — Fase 1

    ⏳ 12b Upload FIT (opcional)

    ⏳ 13b/14b Feed/likes/comentários no frontend/mobile — Fase 2

    ⏳ 15 Fotos de atividade — Fase 2

    ⏳ 16 Perfil público + stats visuais — Fase 2

    ⏳ 17+ Segments, achievements, notificações, análise de treino — Fase 3

Pendências técnicas (dívida para limpar)
Backend

    calories fica NULL no upload GPX — precisa de peso + FC + tipo.

    Sem upload de foto — precisa de storage (S3/Cloudinary/R2).

    Sem rate limiting.

    Redis não usado (está no docker-compose).

    Sem testes automatizados — tests/ vazia.

    UserResponse expõe email e birth_date (só em /auth/me, ok, revisar antes de prod real).

    GET /activities/{id}/comments exige auth — se quiser público, remover Depends(get_current_user).

    Sem /activities/{id}/track — criar no 13a.4.

    Upload GPX síncrono — futuro: fila (arq/Celery/RQ).

    Cold start do Render free tier (~30-50s). Fase 2: subir pro plano pago (~$7/mês).

    ALLOWED_ORIGINS no Render aponta só pra localhost:5173 — atualizar no 13a.5.

    SECRET_KEY local e prod diferentes — JWTs não intercambiáveis (correto por design).

Frontend

    Tipos em src/types/api.ts não são gerados do OpenAPI — sincronizados manualmente. Fase 2: openapi-typescript.

    react-hooks/set-state-in-effect desabilitada no eslint.config.js — falso positivo em reidratação. Revisar quando o plugin amadurecer.

    Sem tratamento global de 401 pós-login — hoje apiFetch limpa token mas não redireciona. Fase 2: interceptor global.

    ActivityCard mostra title ou cai pro formatActivityType — se ambos vazios, mostrar "Atividade" genérico.

    Lista sem paginação visível — useActivities só busca limit=20. Fase 2.

    Sem AppHeader link pra perfil/feed — só "Rumo" + "+ Enviar" + "Sair". Adicionar no 13b.

    Upload sem gestão de "rascunho" — permite navegar pra fora no meio do upload; sem AbortController. Link "Cancelar e voltar" adicionado no 13a.3 (se feito). Polimento completo (confirmar descarte + abort) na Fase 2.

    Erro de rede no upload cai em mutation.error.message ("Failed to fetch") — sem tratamento amigável. Fase 2.

Armadilhas conhecidas (CRÍTICO)
Backend / Python

    bcrypt==4.0.1 obrigatório (4.1+ quebra passlib)

    greenlet==3.1.1 explícito no requirements (Python 3.13)

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso

    include_router sem prefix + @router.post("") = FastAPIError

    ResponseValidationError mascara erro do Pydantic — debugar com TypeAdapter

    selectinload obrigatório quando schema acessa relação em async

    validation_alias no Pydantic pra ORM→JSON com nome diferente

    TYPE_CHECKING pra relationship cross-model sem import circular

    Swagger pré-preenche Form() com "string" literal — validação defensiva no service

    pip install fora da venv cai no Python global

    Pydantic v2: campo str obrigatório rejeita null com Field required. Pra aceitar null, precisa str | None = Field(default=None, ...).

    Model vs banco: editar nullable=True no model sem migração NÃO altera a coluna.

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    Migração com Geometry: adicionar import geoalchemy2 no topo E remover op.create_index do GIST

    WKT LINESTRING: ordem é (lon lat). Ex: LINESTRING(-46.63 -23.55, -46.64 -23.56)

    PostGIS + JSONB redundantes — sempre conferir ST_NPoints(route) == jsonb_array_length(raw_track_points)

    Diferença dev/prod: Docker PG 16.4 + PostGIS 3.4; Neon PG 17.11 + PostGIS 3.5

    ST_AsGeoJSON() retorna GeoJSON válido — usar no 13a.4 pra serializar route

Neon

    PostGIS NÃO vem habilitado por padrão — CREATE EXTENSION IF NOT EXISTS postgis;

    Postgres 18 NÃO tem PostGIS ainda no Neon — usar 17

    Duas connection strings: Pooled (host com -pooler) vs Direct (sem -pooler). Usar Direct com asyncpg

    Formato: postgresql+asyncpg:// (não postgresql://), ssl=require, sem channel_binding

Render

    Blueprint (lê render.yaml), não Website

    Free tier dorme após 15 min — primeira request ~30-50s

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head && — idempotente

    SECRET_KEY com generateValue: true — diferente da local

Frontend / Vite 8 / React 19 / Tailwind 3

    Vite 8 + TS 6: vite-env.d.ts não existe mais — types via tsconfig.app.json → "types": ["vite/client"]

    erasableSyntaxOnly: true — proíbe enum, namespace, parameter properties. Usar as const.

    noUnusedLocals + noUnusedParameters ativos — TS quebra o build com variável/import sem uso.

    Tailwind: fixar em tailwindcss@3 — v4 mudou o CLI.

    react-hooks/set-state-in-effect — falso positivo em setState dentro de useEffect. Desabilitado.

    react-leaflet v5 + React 19: importar "leaflet/dist/leaflet.css" no main.tsx é obrigatório (senão tiles desalinhados).

    React Router v7: pacote continua react-router-dom, API compatível com v6.

    zod v4: @hookform/resolvers precisa ser v5+.

    Backend espera form-urlencoded no login (OAuth2PasswordRequestForm), não JSON.

    FormData no apiFetch: setar Content-Type: multipart/form-data manualmente quebra. Deixar o browser setar.

    npm run dev vs npm run lint vs npm run build: só build roda o ESLint + TS. Dev server sobe mesmo com erro de linter.

    AuthProvider no main.tsx — se faltar, useAuth explode em runtime com useAuth precisa estar dentro de <AuthProvider>. Não pega no build.

    Convenção de exports: componentes = named, páginas = default. Não misturar (bug do 13a.3).

Ambiente / tooling

    .env nunca commitado. .env.local (web) também não.

    Docker Desktop PRECISA estar aberto. docker compose start (não up -d).

    docker compose down -v NUNCA (apaga volume).

    Errno 10061 = Postgres local não está rodando.

    Uvicorn precisa estar em terminal separado.

    _scratch/ no .gitignore.

    PowerShell mostra UTF-8 como Latin-1 — dado íntegro pode parecer corrompido.

    PowerShell curl é alias de Invoke-WebRequest. Usar curl.exe ou Invoke-RestMethod.

    Ordem de rotas no router: estáticas antes das dinâmicas.

    git commit "nothing to commit" — algo já foi commitado antes, ou não está rastreado. Conferir git log + git ls-files <path>.

    npm sempre dentro de web/ — a raiz do monorepo não tem package.json.

Convenções

    Comentários/docstrings em português; nomes em inglês.

    REST com prefixos, response_model sempre.

    HTTPException: 401 (auth), 403 (permissão), 404 (not found), 409 (conflito), 422 (Pydantic), 400 (bad request).

    Commits em português, padrão feat:, fix:, chore:, docs:.

    Blocos incrementais: implementar → testar → commitar.

    Usuário prefere explicações didáticas com o "porquê".

    Chat decide o caminho quando há ambiguidade (não fica perguntando "qual prefere?"). Escolher o padrão de mercado, justificar em 1 linha, seguir.

    Sempre avisar quando estiver perto do limite de contexto e gerar handoff.

Estilo de comunicação preferido

Direto ao ponto, blocos de código prontos para copiar/colar, explicações concisas. Sempre avisar quando estiver perto do limite de contexto.
Usuários de teste
Local (Docker)

    teste@rumo.com / senha12345 (id: 01a0f49c-8e6d-7506-a1c1-1c8c72c50523, username: testuser)

    teste2@rumo.com / senha12345 (id: 01a0f9c4-0552-721d-90ea-e7b0ff9af1e1, username: teste2)

    User1 segue User2

    User2 tem 2 atividades "Corrida do user2" (7000m, 2400s, 450 kcal)

    User1 tem 1 atividade "Corrida matinal" (5000m, 1800s, 320 kcal)

    Activity do user2 para testes de comments: 01a0f9d8-8431-7d78-a943-bc832533454c

    GPX de teste: backend/samples/sample_run.gpx (2345 pontos, ~7.3km caminhada)

    Usuários criados no 13a.1: novo1@rumo.com, novo2@rumo.com (sem full_name)

    [A PREENCHER] — atividade criada via upload no teste do 13a.3 (se houver)

Produção (Neon)

    prod@rumo.com / senha12345 (username: produser)

    prod2@rumo.com / senha12345

Próximo passo (13a.4 — Detalhe + mapa)

Ordem de implementação — backend primeiro:
Backend

    backend/app/schemas/activity.py — adicionar TrackResponse:
    python

    class TrackResponse(BaseModel):
        activity_id: UUID
        type: Literal["LineString"] = "LineString"
        coordinates: list[list[float]]  # [[lon, lat, ele], ...]
        bbox: list[float]  # [minLon, minLat, maxLon, maxLat]
        n_points: int
        simplified: bool = False

    backend/app/services/activity_service.py — get_activity_track(db, user_id, activity_id):

        Busca atividade (só do dono — senão 404)

        Usa ST_AsGeoJSON(route) do PostGIS + ST_NPoints(route) + ST_Envelope(route) (ou calcula bbox das coords)

        Retorna TrackResponse

        Não expor raw_track_points — só geometria

    backend/app/routers/activities.py — GET /activities/{id}/track:

        response_model=TrackResponse

        Protegido, só do dono (404 se não for)

        Declarar DEPOIS de /{activity_id} ou antes? Cuidado com ordem de rotas dinâmicas. /{id}/track é mais específico, declarar depois de /{id} funciona (FastAPI resolve certo). Validar.

Frontend

    web/src/api/activities.ts — getActivityTrack(id)

    web/src/hooks/useActivities.ts — useActivityTrack(id) (query key ["activities","track",id])

    web/src/pages/ActivityDetailPage.tsx — <MapContainer> + <Polyline> + cards de métricas + botão deletar

    web/src/App.tsx — rota /activities/:id protegida

    web/src/components/ActivityCard.tsx — virar <Link to={/activities/${id}}>

Ponto de atenção no Leaflet: o MapContainer precisa de height explícita (ex: h-96), senão não renderiza. E o <Polyline> espera positions no formato [[lat, lng], ...] — o GeoJSON do backend vem [lon, lat, ele], então inverter no frontend. Cuidado com isso.
text


---

## Quando você colar isso no `docs/HANDOFF.md`

1. Substitui o arquivo inteiro pelo bloco acima
2. Preenche o `[A PREENCHER]` do usuário de teste se tiver o UUID da atividade nova
3. Confirma se o "Cancelar e voltar" entrou no `UploadPage.tsx` (o item 19 da dívida técnica menciona isso condicionalmente)
4. Commita:
   ```powershell
   git add docs/HANDOFF.md
   git commit -m "docs: handoff atualizado após 13a.3"
   git push origin main

Pronto pro próximo chat. Abre uma sessão nova, cola o HANDOFF.md atualizado, e a gente começa o 13a.4 pelo backend (TrackResponse + get_activity_track + endpoint).