# HANDOFF — Rumo

Última atualização: 17/10/2026 (pausa após bloco 16)

---

## Visão do produto (NORTE — ler antes de qualquer decisão)

O Rumo é um app de exercício físico ambicioso, semelhante ao Strava. Não é
um projeto de portfólio nem um CRUD de treinos. O objetivo é produção real,
com usuários reais usando no dia a dia.

Quando estiver em dúvida sobre uma decisão técnica, perguntar: **isso
aproxima o Rumo do Strava ou afasta?**

- "Expor raw_track_points no ActivityResponse?" → Não. Endpoint dedicado
  de geometria (`/track`) pra não pesar a listagem.
- "Upload GPX síncrono ou background?" → MVP síncrono; futuro fila (arq/Celery).
- "SQLite pra simplificar?" → Não. PostGIS é obrigatório (Strava é geo-first).

O Rumo **NÃO é**:
- ❌ Projeto de portfólio.
- ❌ CRUD de exercícios.
- ❌ Clone literal do Strava.

O Rumo **É**:
- ✅ Rede social de exercícios.
- ✅ Produto real, em produção.

### Roadmap em fases (vertical slice, não horizontal)

Construir features completas atravessando backend + frontend + mobile,
em vez de terminar o backend inteiro antes de começar o frontend.

**Fase 1 — Deploy + primeira feature visível** ✅ CONCLUÍDA
- Bloco 11: Deploy backend (Render + Neon)
- Bloco 13a: Frontend mínimo (React/Vercel)
- Bloco 13b: Social no frontend completo
- Bloco 13b.7: Perfil completo (backend + frontend)
- Fix: menu mobile (hamburger + drawer)

**Fase 2 — Refinar o que existe** (em andamento)
- ✅ Bloco 16: Perfil + stats visuais (StatsCards + WeeklyChart + filtro)
- ⏳ Bloco 15: Fotos de atividade (precisa escolher storage)
- ⏳ Bloco 12b: Upload FIT (opcional, se houver relógio pra testar)
- ⏳ Bloco 14a: Mobile Flutter mínimo
- ⏳ Bloco 17: Notificações (in-app primeiro, push depois)

**Fase 3 — Diferenciais do Strava** (longo prazo)
- Bloco 18+: segments, leaderboards, achievements, análise de treino

**O que NÃO fazer**: tentar "terminar o backend antes de tudo". Atrasa
meses, mata motivação, ignora que o frontend ensina o backend. O 13b
provou isso (GET /activities/{id} só existia pro dono até o feed expor
a necessidade de abrir pra seguidores). O 13b.7 reforçou (perfil só
mostrava UUID até precisar de username real).

---

## Estado atual do projeto

**Em produção, testado e funcionando:**
- ✅ Auth (register/login/JWT) + reidratação de sessão
- ✅ CRUD de atividades (JSON + upload GPX)
- ✅ Upload GPX com cálculo automático (distância, pace, elevação)
- ✅ Mapa/rota no detalhe (Leaflet, endpoint dedicado `/track`)
- ✅ Splits por km (backend)
- ✅ Follows (seguir/seguidores)
- ✅ Feed (próprias + de quem segue)
- ✅ Likes (kudos) com persistência real no detalhe
- ✅ Comentários (criar, listar, deletar)
- ✅ Perfil público (username/full_name + atividades de outro user com regra de follow)
- ✅ Stats visuais no próprio perfil (4 cards + gráfico semanal + filtro por tipo)
- ✅ Menu mobile (hamburger + drawer) no header
- ✅ Deploy: Render (backend) + Vercel (frontend) + Neon (banco)

**Pendências conhecidas (dívidas, não bloqueiam):**
- `useFollowUser` não invalida `activitiesKeys.lists()` — seção de atividades no perfil de outro user só atualiza no reload após seguir.
- `useUserActivities` fixa `limit=20` — sem paginação visível.
- Bundle 598 kB (warning do Vite) — code splitting com `React.lazy` planejado.
- Stats só no próprio perfil (endpoints `/stats/*` são do current_user — não há endpoint de stats de outro).
- Sem upload de foto — precisa escolher storage (recomendação: Cloudinary free tier).
- Sem rate limiting.
- Redis não usado (está no docker-compose, sem consumidor).
- Sem testes automatizados (`tests/` vazia).
- `UserResponse` expõe email/birth_date (só em `/auth/me`, revisar antes de prod séria).
- `GET /activities/{id}/comments` exige auth — se quiser público, remover `Depends(get_current_user)`.
- Upload GPX síncrono — futuro: fila (arq/Celery/RQ).
- Cold start do Render free tier (~30-50s). Fase 2: subir pro plano pago (~$7/mês).

---

## Stack

### Backend
- Python 3.13.7 + FastAPI + SQLAlchemy 2.0 async + Alembic + GeoAlchemy2
- Banco dev: PostgreSQL 16.4 + PostGIS 3.4 (Docker, `postgis/postgis:16-3.4`)
- Banco prod: Neon (PostGIS habilitado, projeto `rumo`, branch `production`,
  região AWS US East 2 Ohio, PG 17.11 + PostGIS 3.5)
- Cache: Redis (Docker, ainda não usado)
- Deploy: Render (Blueprint via `render.yaml`, free tier)
  - URL: https://rumo-api-5s0b.onrender.com
  - Docs: https://rumo-api-5s0b.onrender.com/docs

### Frontend
- Vite 8.3.4 + React 19.2.8 + TypeScript 6.0.2
- React Router DOM 7.18.4 (SPA, BrowserRouter)
- TanStack Query 5.104.2 (cache/servidor state)
- react-hook-form 7.90.0 + zod 4.6.6 + @hookform/resolvers 5.9.1
- Tailwind CSS 3.4.19 (paleta `rumo` custom + Inter)
- Leaflet 1.9.4 + react-leaflet 5.0.0 (mapas OSM Standard)
- **Recharts 3.7.x + react-is** (gráfico semanal — instalado no bloco 16)
- ESLint 10 (flat config do Vite v9, `react-hooks/set-state-in-effect` desabilitada)
- Deploy: Vercel (Root Directory: `web/`)
  - URL: https://rumo-wheat.vercel.app
  - Env var: `VITE_API_URL=https://rumo-api-5s0b.onrender.com`
  - SPA fallback: `web/vercel.json` com rewrite catch-all

### Repo / IDE / OS
- Repo: https://github.com/mmnc12/rumo (privado)
- IDE: VS Code (terminal integrado)
- OS: Windows (PowerShell)
- Pacote: npm

---

## Estrutura de pastas (atualizada após bloco 16)

D:\Rumo
├── .gitignore, README.md, docker-compose.yml, render.yaml
├── docs\HANDOFF.md
├── backend
│ ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│ ├── _scratch\ (NÃO versionado)
│ ├── samples\ (não versionado — GPX de teste)
│ ├── alembic\env.py + versions
│ ├── app
│ │ ├── main.py, config.py, database.py
│ │ ├── core\security.py, core\dependencies.py
│ │ ├── models{user,activity,follow,like,comment,init}.py
│ │ ├── schemas{user,activity,stats,like,comment,init}.py
│ │ ├── routers{auth,activities,feed,users,comments,init}.py
│ │ └── services{activity_service,gpx_service,stats_service,
│ │ follow_service,like_service,feed_service,
│ │ comment_service,errors,init}.py
│ └── tests
├── mobile\ (vazio — Flutter entra no 14a)
└── web
├── .env.local (não versionado), .env.example
├── .gitignore, eslint.config.js, index.html
├── package.json, package-lock.json, postcss.config.js
├── tailwind.config.js (paleta rumo)
├── tsconfig.json, tsconfig.app.json, tsconfig.node.json
├── vercel.json ← SPA fallback
├── vite.config.ts
└── src
├── api
│ ├── client.ts ← apiFetch + ApiError + token helpers
│ ├── auth.ts ← login/register/getMe
│ ├── activities.ts ← list/get/delete/uploadGpx/getActivityTrack
│ ├── social.ts ← feed/likes/comments/follows/getUser
│ └── stats.ts ← getStatsSummary/getStatsWeekly (bloco 16)
├── components
│ ├── ProtectedRoute.tsx ← named export
│ ├── AppHeader.tsx ← named export + nav desktop + hamburger mobile + drawer
│ ├── ActivityCard.tsx ← named export + author opcional + like otimista
│ ├── LikeButton.tsx ← botão de like real com contagem
│ ├── CommentsSection.tsx ← lista + form + delete
│ ├── StatsCards.tsx ← 4 cards de totais (bloco 16)
│ └── WeeklyChart.tsx ← LineChart Recharts (bloco 16)
├── contexts\AuthContext.tsx ← AuthProvider (named export)
├── hooks
│ ├── useAuth.ts
│ ├── useActivities.ts ← queries + useUploadGpx + useUserActivities + useActivity + useActivityTrack + useDeleteActivity
│ ├── useSocial.ts ← useFeed/useToggleLike/useComments/useFollowUser
│ ├── useProfile.ts ← useFollowers/useFollowing/useIsFollowing/useUser
│ └── useStats.ts ← useStatsSummary/useStatsWeekly (bloco 16)
├── lib\format.ts
├── pages
│ ├── LoginPage.tsx, RegisterPage.tsx ← default export
│ ├── ActivitiesPage.tsx, UploadPage.tsx ← default export
│ ├── ActivityDetailPage.tsx ← + autor + delete só pro dono
│ ├── FeedPage.tsx ← default export
│ └── ProfilePage.tsx ← + username real + atividades + stats (só no próprio)
├── types\api.ts ← espelho dos schemas Pydantic (inclui StatsSummary/StatsPeriod/StatsWeeklyResponse)
├── App.tsx ← rotas
├── main.tsx ← QueryClient + BrowserRouter + AuthProvider
└── index.css


---

## Models existentes (backend)

### User
- id (UUID v7), email (unique), username (unique), full_name (nullable)
- hashed_password, weight_kg, height_cm, birth_date
- is_active, created_at, updated_at (todos DateTime(timezone=True))

### Activity
- id (UUID v7), user_id (FK users CASCADE)
- activity_type (enum: run/walk/cycle/hike/swim/other)
- title, description, started_at (indexed), finished_at, duration_s
- distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps
- route (Geometry LINESTRING 4326), raw_track_points (JSONB)
  - formato `[[lat, lon, ele, unix_ts], ...]`
- created_at, updated_at
- `user = relationship("User", backref="activities", lazy="raise")`

### Follow / Like / Comment
- Inalterados desde o Bloco 10.

---

## Endpoints existentes (backend)

### Auth & Users
- GET / — metadados
- GET /health — status API + banco
- POST /auth/register — cria (201, 409 se duplicado)
- POST /auth/login — form-urlencoded (username=email), retorna JWT
- GET /auth/me — protegido
- POST /users/{user_id}/follow — 204
- DELETE /users/{user_id}/follow — 204
- GET /users/{user_id}/followers?limit&offset — 200, list[UserPublic]
- GET /users/{user_id}/following?limit&offset — 200, list[UserPublic]
- **GET /users/{user_id} — 200, UserPublic (qualquer autenticado) ← 13b.7**

### Activities
- POST /activities — 201 (JSON pré-calculado)
- POST /activities/upload — 201 (multipart, .gpx)
- GET /activities?limit=20&offset=0 — lista próprias
- **GET /activities?user_id= — lista de outro (requer follow; 403 caso contrário) ← 13b.7**
- GET /activities/{id} — dono OU seguidor do dono (404 caso contrário)
- GET /activities/{id}/track — dono OU seguidor do dono
  - GeoJSON-like: `{ activity_id, type: "LineString", coordinates: [[lon,lat],...], bbox: [minLon,minLat,maxLon,maxLat], n_points, simplified }`
- DELETE /activities/{id} — 204 (só o dono — leitura ≠ escrita)
- GET /activities/stats/summary?activity_type=
- GET /activities/stats/weekly?weeks=8&activity_type=
- GET /activities/stats/monthly?months=6&activity_type=
- POST /activities/{id}/like — 200, `{ count, liked_by_me }`
- DELETE /activities/{id}/like — 204
- GET /activities/{id}/likes?limit&offset — 200, `{ count, liked_by_me, users: UserPublic[] }`

### Comments
- POST /activities/{activity_id}/comments — 201, body `{ "content": "..." }` (campo é `content`)
- GET /activities/{activity_id}/comments?limit&offset — 200, `list[CommentResponse]` (array direto, autor aninhado em `author`)
- DELETE /comments/{comment_id} — 204 (só o autor)

### Feed
- GET /feed?limit=20&offset=0 — 200, `list[FeedItemResponse]` (array direto)
  - `FeedItemResponse = ActivityResponse + author: UserPublic` (`validation_alias="user"`)

---

## Frontend — padrões e decisões

### `web/` como monorepo
- Vercel aponta pra `web/` (Root Directory). Render continua em `backend/`.
- `.env.local` NUNCA versionado.
- `vercel.json` dentro de `web/` (não na raiz do monorepo).

### Cliente HTTP (`src/api/client.ts`)
- `apiFetch<T>(path, options)` — única porta pro backend.
- Injeta JWT do `localStorage` (`rumo.token`) automaticamente.
- `body` (objeto) → JSON. `rawBody` (FormData/URLSearchParams) → passa cru.
- FormData NÃO seta `Content-Type` manualmente (browser põe com boundary).
- 401 limpa token automaticamente (força novo login).
- Erros viram `ApiError(status, detail)` — `detail` é o cru do FastAPI.

### Auth (`AuthContext` + `useAuth` + `ProtectedRoute`)
- Token em `localStorage`; user em memória.
- Boot do app chama `GET /auth/me` se houver token (reidrata sessão).
- `register()` faz login automático depois do cadastro.
- `ProtectedRoute` redireciona pra `/login` guardando `state.from`.
- `<AuthProvider>` PRECISA envolver `<App>` no `main.tsx` — erro runtime se faltar.

### Rotas atuais (`App.tsx`)
- `/login`, `/register` (públicas)
- `/activities` (protegida) — lista próprias
- `/feed` (protegida) — feed social
- `/upload` (protegida)
- `/activities/:id` (protegida) — detalhe (dono ou seguidor)
- `/users/:id` (protegida) — perfil (UUID; não há slug por username)
- `/` → redireciona pra `/activities`
- `*` → 404 simples

### Convenção de exports (IMPORTANTE — não misturar)
- **Componentes reutilizáveis** → named export (`export function X`)
  - `AppHeader`, `ProtectedRoute`, `ActivityCard`, `LikeButton`,
    `CommentsSection`, `StatsCards`, `WeeklyChart`
- **Páginas** → default export (`export default function X`)
  - `ActivitiesPage`, `UploadPage`, `LoginPage`, `RegisterPage`,
    `ActivityDetailPage`, `FeedPage`, `ProfilePage`

Já custou bug de build no 13a.3 (ProtectedRoute importado como default).

### Query keys (TanStack)
- `activitiesKeys` (`useActivities.ts`):
  - `.all`, `.lists()`, `.list({ limit?, offset?, userId? })`, `.details()`,
    `.detail(id)`, `.tracks()`, `.track(id)`
- `socialKeys` (`useSocial.ts`):
  - `.feed(limit, offset)`, `.likes(activityId)`, `.comments(activityId)`,
    `.followers(userId)`, `.following(userId)`
- **`statsKeys` (`useStats.ts`)**:
  - `.all`, `.summary(activityType?)`, `.weekly(weeks, activityType?)`
- `["users", userId]` (inline em `useUser`) — perfil público.
- `staleTime`:
  - 30s em listas/feed/atividades
  - 5min em track e `useUser`
  - **60s em stats**
- `retry: 1`, `refetchOnWindowFocus: false`.

### Social (13b + 13b.7)
- `useFeed` → `["feed", { limit, offset }]`, `staleTime` 30s.
- `useToggleLike` → otimista com `onMutate/onError/onSettled`. **NÃO invalida o feed** no `onSettled` (feed não tem contagem — invalidar causaria refetch de 20 atividades por clique). Só invalida `["likes", id]`.
- `useFollowUser` → invalida `["feed"]` + `["followers", id]` + `["following", id]`. **NÃO invalida `activitiesKeys.lists()`** (dívida).
- `useIsFollowing` → busca `GET /users/{me.id}/following` e checa se o alvo está lá (1 request extra; não existe `GET /users/{id}/is-following`).
- Botão de like no card (`ActivityCard`): estado local, não persiste no reload.
- Botão de like no detalhe (`LikeButton`): busca `GET /likes` real, persiste.
- Clique no coração dentro do `<Link>`: `e.preventDefault()` + `e.stopPropagation()`.

### Perfil (13b.7 + 16)
- `ProfilePage` usa `useUser(id)` (username/full_name reais) + `useUserActivities(id)` (lista) + `useIsFollowing` + `useFollowUser`.
- **Stats só aparecem se `isSelf === true`** (`useStatsSummary`/`useStatsWeekly` recebem `enabled = isSelf`).
- Filtro por tipo (`TYPE_FILTERS`): `undefined` (Tudo), `run`, `walk`, `cycle`, `hike`, `swim`.
- 403 de `useUserActivities` → CTA "Siga @username pra ver as atividades dele(a)".
- Stats: 4 cards (atividades, distância, tempo, elevação) + `WeeklyChart` (LineChart em km, últimas 8 semanas).

### Formatters (`src/lib/format.ts`)
- `formatDistance(m)`, `formatDuration(s)`, `formatPace(sPerKm)`,
  `formatSpeed(mps)`, `formatDateTime(iso)`, `formatRelativeDate(iso)`,
  `formatActivityType("run")`, `activityEmoji("run")`

### Tailwind
- Paleta custom: `rumo-50 … rumo-900` (laranja). Primária: `rumo-500 = #f97316`.
- Fonte: Inter. Body: `bg-gray-50 text-gray-900 antialiased`.
- **Cor hardcoded no Recharts**: `#f97316` (mesma laranja) — se mudar a paleta, atualizar em `WeeklyChart.tsx`.

### Tipos (`src/types/api.ts`)
- `ActivityType`, `UserPublic`, `UserResponse`, `Activity`, `TokenResponse`,
  `ValidationErrorDetail`, `TrackResponse`, `FeedItem`, `LikeState`, `LikeList`,
  `Comment`, **`StatsSummary`, `StatsPeriod`, `StatsWeeklyResponse`, `StatsMonthlyResponse`**
- `UserPublic` tem `{ id, username, full_name, is_active }`.
- `Comment` tem `{ id, activity_id, content, created_at, updated_at, author }`.
- Interface da atividade se chama `Activity` (não `ActivityResponse`) — espelho local do Pydantic. Fase 2: gerar via OpenAPI.
- **`StatsPeriod` tem `period_start: string` (ISO "YYYY-MM-DD")**, `total_distance_m`, `total_duration_s`, `total_activities`, `total_calories`. Não tem campo de data completa.

---

## Produção (Render + Neon + Vercel)

### Backend
- API: https://rumo-api-5s0b.onrender.com
- Deploy: `git push origin main` → Render rebuilda → `alembic upgrade head` → gunicorn (2 workers uvicorn).
- Free tier dorme após 15 min. Primeira request ~30-50s.
- Env vars no Render: `DATABASE_URL`, `ENVIRONMENT=production`,
  `DEBUG=false`, `SECRET_KEY`, `ALGORITHM=HS256`,
  `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `PYTHON_VERSION=3.13.7`
- `ALLOWED_ORIGINS` (JSON, `list[str]`):
  ```json
  ["http://localhost:5173","https://rumo-wheat.vercel.app"]

Frontend

    App: https://rumo-wheat.vercel.app

    Deploy: git push origin main → Vercel rebuilda (~1min).

    Root Directory: web/.

    Env var: VITE_API_URL=https://rumo-api-5s0b.onrender.com.

    SPA fallback: web/vercel.json com { "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }.

Workflow de teste (padrão atual)

Testar direto em produção, não local. Build local (npm run build) só
pra garantir TS/ESLint limpos antes do push. Motivo: o sistema já está no ar,
subir Docker + uvicorn + vite local é overhead sem ganho proporcional.
Blocos concluídos

    ✅ 1 a 9 (auth, CRUD, GPX, stats backend)

    ✅ 10a Follows / 10b Feed / 10c Likes / 10d Comentários (backend)

    ✅ 11 Deploy Render + Neon

    ✅ 12 Upload GPX backend

    ✅ 13a.0 a 13a.5 (frontend mínimo completo, deploy Vercel)

    ✅ 13b.1 a 13b.6 (social no frontend)

    ✅ 13b.7 Perfil completo:

        GET /users/{user_id} (UserPublic, qualquer autenticado)

        GET /activities?user_id= (requer follow; 403 caso contrário)

        ProfilePage com username/full_name reais + lista de atividades + CTA 403

        ActivityDetailPage com bloco "por @autor" + delete só pro dono

    ✅ Fix: menu mobile (hamburger + drawer, fecha em link/backdrop/Esc)

    ✅ 16 Perfil + stats visuais:

        StatsCards: 4 cards (atividades, distância, tempo, elevação)

        WeeklyChart: LineChart Recharts (km por semana, últimas 8)

        Filtro por tipo (run/walk/cycle/hike/swim) — só no próprio perfil

        Deps: recharts@3.7 + react-is (peer)

Blocos pendentes

    ⏳ 15 Fotos de atividade — Fase 2, próxima recomendação. Escolher storage (Cloudinary free tier é o mais simples).

    ⏳ 12b Upload FIT — opcional, se houver relógio Garmin/Polar pra testar.

    ⏳ 14a Mobile Flutter — Fase 2, mas teste mobile do site atual já passou (menu funciona, fluxos OK). Flutter fica pra quando o site no celular não bastar.

    ⏳ 17 Notificações — Fase 3.

    ⏳ 18+ Segments, leaderboards, achievements, análise de treino — Fase 3.

Recomendação de ordem (retomada)

Bloco 15 (fotos de atividade) — próximo grande passo.

Escopo:

    Backend: novo model ActivityPhoto (activity_id FK, url, created_at). Endpoint POST /activities/{id}/photos (upload multipart) + GET /activities/{id}/photos + DELETE /photos/{id}.

    Storage: Cloudinary free tier (25 GB/mês) — upload direto do backend, sem configurar bucket AWS. Alternativa: Cloudflare R2 (S3-compatible, free tier generoso).

    Frontend: upload no ActivityDetailPage (dono), grid/carrossel no detalhe, foto principal no ActivityCard do feed.

    DB: migração Alembic (tabela nova, sem alterar existentes).

Depois do 15:

    12b FIT só se tiver relógio pra testar.

    14a Flutter quando o site no celular não bastar (teste mobile atual passou sem queixas).

    17 Notificações (in-app primeiro).

    18+ Segments — o que mais aproxima o Rumo do Strava.

Pendências técnicas (dívida para limpar)
Backend

    GET /activities/{id} agora aceita dono OU seguidor. Decisão de produto em aberto: permitir "qualquer autenticado" (atividade pública)? Introduzir is_public no model?

    GET /activities/{id} não aninha author — o detalhe busca via useUser(user_id) no frontend (2 requests). Se virar gargalo, aninhar no backend.

    calories fica NULL no upload GPX (precisa peso + FC + tipo).

    Sem upload de foto (bloco 15).

    Sem rate limiting.

    Redis não usado (está no docker-compose).

    Sem testes automatizados (tests/ vazia).

    UserResponse expõe email e birth_date (só em /auth/me, ok, revisar antes de prod séria).

    GET /activities/{id}/comments exige auth — se quiser público, remover Depends(get_current_user).

    Upload GPX síncrono — futuro: fila (arq/Celery/RQ).

    Cold start do Render free tier (~30-50s). Fase 2: subir pro plano pago (~$7/mês).

    SECRET_KEY local e prod diferentes — JWTs não intercambiáveis (correto por design).

    GET /activities/stats/* só funciona pro current_user — não há endpoint de stats de outro usuário. Perfil de outro user não mostra stats (design atual do 16).

Frontend

    useFollowUser não invalida activitiesKeys.lists() — seção de atividades do perfil só atualiza no reload após seguir. Fix de 1 linha em useSocial.ts (adicionar queryClient.invalidateQueries({ queryKey: activitiesKeys.lists() }) no onSuccess).

    useUserActivities fixa limit=20 — sem paginação visível.

    Contagem de likes no card do feed é local (não persiste no reload). Só o detalhe tem contagem real.

    Menu mobile resolvido (hamburger + drawer). Desktop sem regressão.

    Perfil no mobile: link do username no header é hidden sm:inline — no mobile, acesso ao perfil via drawer agora funciona.

    Mapa sem layer switcher (só OSM Standard). Adicionar toggle Standard/Satélite (Esri World Imagery) na Fase 2.

    Tipos em src/types/api.ts não são gerados do OpenAPI — sincronizados manualmente. Fase 2: openapi-typescript.

    react-hooks/set-state-in-effect desabilitada no ESLint — falso positivo em reidratação. Revisar quando o plugin amadurecer.

    Sem tratamento global de 401 pós-login — hoje apiFetch limpa token mas não redireciona. Fase 2: interceptor global.

    client.ts: as string no VITE_API_URL — cast desnecessário; o if (!API_URL) já faz narrowing.

    ActivityCard mostra title ou cai pra formatActivityType — se ambos vazios, mostrar "Atividade" genérico.

    Upload sem gestão de "rascunho" — permite navegar pra fora no meio do upload; sem AbortController.

    Erro de rede no upload cai em mutation.error.message ("Failed to fetch") — sem tratamento amigável.

    Bundle 598 kB (warning do Vite) — code splitting com React.lazy nas rotas pesadas (Leaflet só em /activities/:id) é o próximo passo natural de otimização. Ganho real: primeiro load pra ~250 kB.

Infra / deploy

    vercel.json PRECISA estar em web/ (Root Directory do Vercel é web/). Na raiz do monorepo o Vercel ignora silenciosamente.

    Preview deploys do Vercel (cada PR gera URL) vão precisar de CORS. Hoje só Production está em ALLOWED_ORIGINS.

Armadilhas conhecidas (CRÍTICO)
Backend / Python

    bcrypt==4.0.1 obrigatório (4.1+ quebra passlib).

    greenlet==3.1.1 explícito no requirements (Python 3.13).

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7.

    DateTime sem timezone=True — bug silencioso.

    include_router sem prefix + @router.post("") = FastAPIError.

    ResponseValidationError mascara erro do Pydantic — debugar com TypeAdapter.

    selectinload obrigatório quando schema acessa relação em async.

    validation_alias no Pydantic pra ORM→JSON com nome diferente (ex: author: UserPublic = Field(validation_alias="user")).

    TYPE_CHECKING pra relationship cross-model sem import circular.

    Swagger pré-preenche Form() com "string" literal — validação defensiva no service.

    pip install fora da venv cai no Python global.

    Ativar venv antes de rodar uvicorn: .\venv\Scripts\Activate.ps1 (ou python -m uvicorn se o PATH já resolver). Prompt muda pra (venv) PS ....

    Pydantic v2: campo str obrigatório rejeita null com "Field required". Pra aceitar null, precisa str | None = Field(default=None, ...).

    Model vs banco: editar nullable=True no model sem migração NÃO altera a coluna.

    Pydantic Settings + list[str]: valor da env var é parseado via json.loads. Aspas tipográficas (" ") em vez de retas (" ") quebram com SettingsError: error parsing value for field "ALLOWED_ORIGINS". Fix: digitar as aspas manualmente.

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py.

    Migração com Geometry: adicionar import geoalchemy2 no topo E remover op.create_index do GIST.

    WKT LINESTRING: ordem é (lon lat). Ex: LINESTRING(-46.63 -23.55, -46.64 -23.56).

    PostGIS + JSONB redundantes — sempre conferir ST_NPoints(route) == jsonb_array_length(raw_track_points).

    Diferença dev/prod: Docker PG 16.4 + PostGIS 3.4; Neon PG 17.11 + PostGIS 3.5.

    ST_AsGeoJSON() retorna string JSON — json.loads() no service. Em alguns casos o driver asyncpg devolve dict direto — defensivamente, checar isinstance(x, dict).

Neon

    PostGIS NÃO vem habilitado por padrão — CREATE EXTENSION IF NOT EXISTS postgis;.

    Postgres 18 NÃO tem PostGIS ainda no Neon — usar 17.

    Duas connection strings: Pooled (host com -pooler) vs Direct (sem -pooler). Usar Direct com asyncpg.

    Formato: postgresql+asyncpg:// (não postgresql://), ssl=require, sem channel_binding.

Render

    Blueprint (lê render.yaml), não Website.

    Free tier dorme após 15 min — primeira request ~30-50s.

    rootDir: backend no render.yaml.

    startCommand com alembic upgrade head && — idempotente.

    SECRET_KEY com generateValue: true — diferente da local.

Vercel

    vercel.json vai no Root Directory configurado (aqui: web/), NÃO na raiz do monorepo.

    SPA fallback obrigatório: sem rewrite catch-all → /index.html, F5 em rota interna dá 404 do Vercel.

    Se cleanUrls: true, o destino do rewrite é /index (sem .html).

    Env vars VITE_* só são expostas ao código client-side. Prefixo obrigatório.

Frontend / Vite 8 / React 19 / Tailwind 3

    Vite 8 + TS 6: vite-env.d.ts não existe mais — types via tsconfig.app.json → "types": ["vite/client"].

    erasableSyntaxOnly: true — proíbe enum, namespace, parameter properties. Usar as const.

    noUnusedLocals + noUnusedParameters ativos — TS quebra o build com variável/import sem uso.

    Tailwind: fixar em tailwindcss@3 — v4 mudou o CLI.

    react-hooks/set-state-in-effect — falso positivo em setState dentro de useEffect. Desabilitado.

    react-leaflet v5 + React 19: importar "leaflet/dist/leaflet.css" no main.tsx é obrigatório (senão tiles desalinhados).

    MapContainer precisa de height explícita (ex: style={{ height: "24rem" }}) — senão não renderiza.

    <Polyline> espera [[lat, lng], ...] — GeoJSON do backend vem [lon, lat]. Inverter no frontend.

    React Router v7: pacote continua react-router-dom, API compatível com v6.

    zod v4: @hookform/resolvers precisa ser v5+.

    Backend espera form-urlencoded no login (OAuth2PasswordRequestForm), não JSON.

    FormData no apiFetch: NÃO setar Content-Type: multipart/form-data manualmente. Deixar o browser setar (com boundary).

    npm run dev vs npm run lint vs npm run build: só build roda ESLint + TS. Dev server sobe mesmo com erro de linter.

    <AuthProvider> no main.tsx — se faltar, useAuth explode em runtime. Não pega no build.

    Convenção de exports: componentes = named, páginas = default. Não misturar.

    Link dentro de <Link>: HTML inválido. Solução no ActivityCard: o <Link> que navega fica dentro de um <div> wrapper; o autor (<Link>) fica fora do <Link> principal (acima). Quando precisa aninhar (like no card), o botão fica dentro do <Link> mas usa e.preventDefault() + e.stopPropagation() no onClick.

    NavLink em vez de Link no header: pra rota ativa ter destaque (isActive no className).

    Recharts 3.x: react-is virou peerDependency — precisa instalar (npm install recharts react-is). Sem isso, build quebra com Cannot find module 'react-is'.

    Recharts ResponsiveContainer: precisa de pai com height explícita (style={{ height: "16rem" }}). Sem isso, colapsa a 0px.

    Recharts LineChart com 1 ponto: desenha só o dot (a linha some). Não é bug.

    StatsCards / WeeklyChart: cuidado ao importar formatPace/formatDistance — se não usar, TS quebra o build. Remover import órfão.

Ambiente / tooling

    .env nunca commitado. .env.local (web) também não.

    Docker Desktop PRECISA estar aberto. docker compose start (não up -d).

    docker compose down -v NUNCA (apaga volume).

    Errno 10061 = Postgres local não está rodando.

    Uvicorn precisa estar em terminal separado.

    _scratch/ no .gitignore.

    PowerShell mostra UTF-8 como Latin-1 — dado íntegro pode parecer corrompido (Ã¡, Ã§, Гўв‚¬В¦). O arquivo no disco provavelmente está OK. Se reescrever pra "corrigir", garantir que o editor salva em UTF-8 (VS Code: canto inferior direito).

    uvicorn não reconhecido no PowerShell: venv não ativada. .\venv\Scripts\Activate.ps1 (ou python -m uvicorn app.main:app --reload). Se der erro de execution policy, Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass antes.

    PowerShell curl é alias de Invoke-WebRequest. Usar curl.exe ou Invoke-RestMethod.

    Ordem de rotas no router: estáticas antes das dinâmicas (exceto quando o path tem segmentos diferentes — aí não importa).

    git commit "nothing to commit" — algo já foi commitado antes, ou não está rastreado. Conferir git log + git ls-files <path>.

    npm sempre dentro de web/ — a raiz do monorepo não tem package.json.

    VS Code desatualizado: erro ts(2307) (módulo não encontrado) com arquivo existente → Ctrl+Shift+P → "TypeScript: Restart TS Server". O npm run build no terminal resolve se for real.

Workflow preferido pelo usuário (NOVO)

    Testar direto em produção (Render + Vercel) — o sistema já está no ar. Build local só pra garantir TS/ESLint limpos antes do push. Subir Docker + uvicorn + vite local é overhead sem ganho proporcional.

    Sempre seguir a recomendação do chat — não oferecer A/B/C, escolher o padrão de mercado, justificar em 1 linha, seguir.

    Avisar quando o contexto estiver perto do limite e gerar handoff completo.

    Handoff completo só quando o contexto apertar — não interromper o fluxo de trabalho pra gerar handoff parcial.

Convenções

    Comentários/docstrings em português; nomes em inglês.

    REST com prefixos, response_model sempre.

    HTTPException: 401 (auth), 403 (permissão), 404 (not found), 409 (conflito), 422 (Pydantic), 400 (bad request).

    Commits em português, padrão feat:, fix:, chore:, docs:.

    Blocos incrementais: implementar → testar (em prod) → commitar.

    Usuário prefere explicações didáticas com o "porquê".

    Chat decide o caminho quando há ambiguidade (não fica perguntando "qual prefere?"). Escolher o padrão de mercado, justificar em 1 linha, seguir.

Estilo de comunicação preferido

Direto ao ponto, blocos de código prontos para copiar/colar, explicações concisas. Sempre avisar quando estiver perto do limite de contexto.
Usuários de teste
Produção (Neon) — usados agora

    prod@rumo.com / senha12345 (username: produser)

    prod2@rumo.com / senha12345

    (Se prod2 não existir mais, registrar de novo ou criar prod3@rumo.com)

Local (Docker) — não usados no workflow atual

    teste@rumo.com / senha12345 (id: 01a0f49c-8e6d-7506-a1c1-1c8c72c50523, username: testuser)

    teste2@rumo.com / senha12345 (id: 01a0f9c4-0552-721d-90ea-e7b0ff9af1e1, username: teste2)

    User1 segue User2.

    User2 tem 2 atividades "Corrida do user2" (7000m, 2400s, 450 kcal).

    User1 tem 1 atividade "Corrida matinal" (5000m, 1800s, 320 kcal).

    GPX de teste: backend/samples/sample_run.gpx (2345 pontos, ~7.3km caminhada).

Próximo passo (recomendado)

Bloco 15 — Fotos de atividade.

Escopo:

    Storage: Cloudinary free tier (25 GB/mês) — upload direto do backend, sem configurar bucket AWS. Alternativa: Cloudflare R2 (S3-compatible, free tier generoso).

        Env vars no Render: CLOUDINARY_URL (formato cloudinary://API_KEY:API_SECRET@CLOUD_NAME).

        SDK: cloudinary (Python) no backend.

    Backend:

        Model ActivityPhoto (id UUID v7, activity_id FK CASCADE, url, public_id (pra deletar), created_at).

        Migração Alembic.

        Endpoints:

            POST /activities/{id}/photos — upload multipart (só o dono). Retorna ActivityPhotoResponse.

            GET /activities/{id}/photos — lista (qualquer autenticado que possa ver a atividade).

            DELETE /photos/{photo_id} — só o dono.

        Validação: tipo (jpeg/png/webp), tamanho (limite 10 MB).

    Frontend:

        api/photos.ts — upload/get/delete.

        hooks/usePhotos.ts — useActivityPhotos, useUploadPhoto, useDeletePhoto.

        ActivityDetailPage: grid de fotos abaixo do mapa (com botão de upload pro dono).

        ActivityCard: primeira foto como thumbnail (se existir).

        Componente PhotoGallery (grid responsivo, modal/lightbox simples no clique).

Antes de começar o 15: criar conta no Cloudinary e pegar CLOUDINARY_URL. Configurar env var no Render.

Alternativa se preferir backend-first: 12b (FIT) — só se tiver relógio Garmin/Polar pra testar. Sem hardware, é desenvolvimento no escuro. Não recomendado.

Não recomendado agora: 14a (Flutter) — o site no celular está funcional (menu mobile OK, fluxos testados). Flutter fica pra quando o site no celular não bastar.
Fixes rápidos pendentes (se bater vontade)

    Invalidar activitiesKeys.lists() no useFollowUser (1 linha em useSocial.ts):
    ts

    queryClient.invalidateQueries({ queryKey: activitiesKeys.lists() });

    No onSuccess do useFollowUser. Faz a seção de atividades do perfil de outro user atualizar após seguir (sem reload).

    Silenciar warning do Vite (1 linha em vite.config.ts):
    ts

    build: { chunkSizeWarningLimit: 800 }

    Só esconde o aviso. Não resolve o problema real (bundle 598 kB).

    Code splitting real (~30 min, Fase 2):
    React.lazy() + Suspense nas rotas. Leaflet só carrega em /activities/:id. Ganho: primeiro load pra ~250 kB.

Teste mobile — resultado

Feito. Menu mobile funcionando (hamburger + drawer). Navegação OK, feed OK, perfil OK, detalhe OK, mapa com pinch-to-zoom OK. Decisão 14a vs 16 resolvida: Flutter fica pra depois, site no celular é usável como MVP mobile.


---

## Como retomar (para o próximo chat)

Cola o conteúdo de `docs/HANDOFF.md` (o bloco acima) e diga:

> "Retomando o Rumo. Handoff anexo. Vamos começar o bloco 15 (fotos de atividade)."

O próximo chat já sabe:

- Onde paramos (bloco 16 concluído em produção).
- Próximo passo recomendado (15 fotos, com Cloudinary).
- Todas as armadilhas e padrões do projeto.
- Que **testar em produção** é o workflow atual.
- Que **sempre seguir a recomendação do chat** (não oferecer A/B/C).

