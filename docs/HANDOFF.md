Visão do produto (NORTE — ler antes de qualquer decisão)

O Rumo é um app de exercício físico ambicioso, semelhante ao Strava. Não é
um projeto de portfólio nem um CRUD de treinos. O objetivo é produção real,
com usuários reais usando no dia a dia.

Quando estiver em dúvida sobre uma decisão técnica, perguntar: isso
aproxima o Rumo do Strava ou afasta?

    "Expor raw_track_points no ActivityResponse?" → Não. Endpoint dedicado
    de geometria (/track) pra não pesar a listagem.

    "Upload GPX síncrono ou background?" → MVP síncrono; futuro fila (arq/Celery).

    "SQLite pra simplificar?" → Não. PostGIS é obrigatório (Strava é geo-first).

O Rumo NÃO é:

    ❌ Projeto de portfólio.

    ❌ CRUD de exercícios.

    ❌ Clone literal do Strava.

O Rumo É:

    ✅ Rede social de exercícios.

    ✅ Produto real, em produção.

Roadmap em fases (vertical slice, não horizontal)

Construir features completas atravessando backend + frontend + mobile,
em vez de terminar o backend inteiro antes de começar o frontend.

Fase 1 — Deploy + primeira feature visível ✅ CONCLUÍDA

    Bloco 11: Deploy backend (Render + Neon)

    Bloco 13a: Frontend mínimo (React/Vercel)

    Bloco 13b: Social no frontend completo

    Bloco 13b.7: Perfil completo (backend + frontend)

    Fix: menu mobile (hamburger + drawer)

Fase 2 — Refinar o que existe (em andamento)

    ✅ Bloco 16: Perfil + stats visuais (StatsCards + WeeklyChart + filtro)

    ✅ Bloco 15: Fotos de atividade (backend + frontend + Cloudinary)

    ✅ Fixes rápidos: enquadramento das fotos + invalidação no follow

    ⏳ Bloco 17: Notificações (in-app primeiro, push depois) ← próximo recomendado

    ⏳ Bloco 12b: Upload FIT (opcional, se houver relógio pra testar)

    ⏳ Bloco 14a: Mobile Flutter mínimo

Fase 3 — Diferenciais do Strava (longo prazo)

    Bloco 18+: segments, leaderboards, achievements, análise de treino

O que NÃO fazer: tentar "terminar o backend antes de tudo". Atrasa
meses, mata motivação, ignora que o frontend ensina o backend. O 13b
provou isso (GET /activities/{id} só existia pro dono até o feed expor
a necessidade de abrir pra seguidores). O 13b.7 reforçou (perfil só
mostrava UUID até precisar de username real). O 15 reforçou de novo
(fotos só entraram quando o detalhe pediu).
Estado atual do projeto

Em produção, testado e funcionando:

    ✅ Auth (register/login/JWT) + reidratação de sessão

    ✅ CRUD de atividades (JSON + upload GPX)

    ✅ Upload GPX com cálculo automático (distância, pace, elevação)

    ✅ Mapa/rota no detalhe (Leaflet, endpoint dedicado /track)

    ✅ Splits por km (backend)

    ✅ Follows (seguir/seguidores)

    ✅ Feed (próprias + de quem segue)

    ✅ Likes (kudos) com persistência real no detalhe

    ✅ Comentários (criar, listar, deletar)

    ✅ Perfil público (username/full_name + atividades de outro user com regra de follow)

    ✅ Stats visuais no próprio perfil (4 cards + gráfico semanal + filtro por tipo)

    ✅ Menu mobile (hamburger + drawer) no header

    ✅ Fotos de atividade (bloco 15):

        Upload multipart via Cloudinary (backend)

        Galeria no detalhe (grid uniforme aspect-square + lightbox + delete pro dono)

        Storage: Cloudinary free tier (cloud name bmmu9a3y)

    ✅ Fixes rápidos pós-15:

        Enquadramento das fotos na galeria (aspect-square + object-cover — grid uniforme, sem cortes desproporcionais)

        useFollowUser invalida activitiesKeys.lists() — seção de atividades no perfil de outro user atualiza sem reload após seguir

    ✅ Deploy: Render (backend) + Vercel (frontend) + Neon (banco) + Cloudinary (imagens)

Pendências conhecidas (dívidas, não bloqueiam):

    Thumbnail de foto no ActivityCard do feed — não implementado. Recomendação: só fazer quando o backend expuser cover_photo_url ou photo_count no ActivityResponse (evita 20 requests por feed).

    useUserActivities fixa limit=20 — sem paginação visível.

    Bundle 598 kB (warning do Vite) — code splitting com React.lazy planejado.

    Stats só no próprio perfil (endpoints /stats/* são do current_user).

    GET /activities/{id}/photos não valida se o usuário pode ver a atividade — qualquer autenticado que saiba o UUID lista fotos. Dívida consciente (mesma linha do "decisão de produto em aberto").

    Upload de foto é síncrono — cloudinary.uploader.upload bloqueia o event loop ~1–3s. Aceitável no MVP; Fase 3: run_in_threadpool ou fila.

    Delete de foto no Cloudinary silencia exceção — se o Cloudinary falhar, a foto some do banco mas fica órfã no Cloudinary. Fase 3: job de limpeza.

    Sem rate limiting.

    Redis não usado (está no docker-compose, sem consumidor).

    Sem testes automatizados (tests/ vazia).

    UserResponse expõe email/birth_date (só em /auth/me, revisar antes de prod séria).

    GET /activities/{id}/comments exige auth — se quiser público, remover Depends(get_current_user).

    Upload GPX síncrono — futuro: fila (arq/Celery/RQ).

    Cold start do Render free tier (~30-50s). Fase 2: subir pro plano pago (~$7/mês).

Stack
Backend

    Python 3.13.7 + FastAPI + SQLAlchemy 2.0 async + Alembic + GeoAlchemy2

    Banco dev: PostgreSQL 16.4 + PostGIS 3.4 (Docker, postgis/postgis:16-3.4)

    Banco prod: Neon (PostGIS habilitado, projeto rumo, branch production,
    região AWS US East 2 Ohio, PG 17.11 + PostGIS 3.5)

    Cache: Redis (Docker, ainda não usado)

    Storage de imagens: Cloudinary (free tier, cloud name bmmu9a3y)

        Env var no Render: CLOUDINARY_URL (formato cloudinary://API_KEY:API_SECRET@CLOUD_NAME)

        SDK Python: cloudinary>=1.41.0 (instalado na venv: 1.46.3)

        Pasta de upload: rumo/activities/{activity_id}

    Deploy: Render (Blueprint via render.yaml, free tier)

        URL: https://rumo-api-5s0b.onrender.com

        Docs: https://rumo-api-5s0b.onrender.com/docs

Frontend

    Vite 8.3.4 + React 19.2.8 + TypeScript 6.0.2

    React Router DOM 7.18.4 (SPA, BrowserRouter)

    TanStack Query 5.104.2 (cache/servidor state)

    react-hook-form 7.90.0 + zod 4.6.6 + @hookform/resolvers 5.9.1

    Tailwind CSS 3.4.19 (paleta rumo custom + Inter)

    Leaflet 1.9.4 + react-leaflet 5.0.0 (mapas OSM Standard)

    Recharts 3.7.x + react-is (gráfico semanal)

    ESLint 10 (flat config do Vite v9, react-hooks/set-state-in-effect desabilitada)

    Deploy: Vercel (Root Directory: web/)

        URL: https://rumo-wheat.vercel.app

        Env var: VITE_API_URL=https://rumo-api-5s0b.onrender.com

        SPA fallback: web/vercel.json com rewrite catch-all

Repo / IDE / OS

    Repo: https://github.com/mmnc12/rumo (privado)

    IDE: VS Code (terminal integrado)

    OS: Windows (PowerShell)

    Pacote: npm

    Atenção: a venv do backend é D:\Rumo\backend\.venv (com ponto), não venv.

Estrutura de pastas (atualizada após bloco 15 + fixes)

D:\Rumo
├── .gitignore, README.md, docker-compose.yml, render.yaml
├── docs\HANDOFF.md
├── backend
│ ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│ ├── .venv\ (com ponto — ativar com .\.venv\Scripts\Activate.ps1)
│ ├── _scratch\ (NÃO versionado)
│ ├── samples\ (não versionado — GPX de teste)
│ ├── alembic\env.py + versions
│ │ └── 3735c1f73cc7_add_activity_photos.py ← bloco 15
│ ├── app
│ │ ├── main.py, config.py, database.py
│ │ ├── core\security.py, core\dependencies.py
│ │ ├── models{user,activity,activity_photo,follow,like,comment,init}.py
│ │ ├── schemas{user,activity,stats,like,comment,photo,init}.py
│ │ ├── routers{auth,activities,feed,users,comments,photos,init}.py
│ │ └── services{activity_service,gpx_service,stats_service,
│ │ follow_service,like_service,feed_service,comment_service,
│ │ photo_service,errors,init}.py
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
│ ├── stats.ts ← getStatsSummary/getStatsWeekly
│ └── photos.ts ← list/upload/delete (bloco 15)
├── components
│ ├── ProtectedRoute.tsx ← named export
│ ├── AppHeader.tsx ← named export + nav desktop + hamburger mobile + drawer
│ ├── ActivityCard.tsx ← named export + author opcional + like otimista
│ ├── LikeButton.tsx ← botão de like real com contagem
│ ├── CommentsSection.tsx ← lista + form + delete
│ ├── StatsCards.tsx ← 4 cards de totais
│ ├── WeeklyChart.tsx ← LineChart Recharts
│ ├── PhotoGallery.tsx ← grid aspect-square + lightbox + delete (bloco 15)
│ └── PhotoUpload.tsx ← input file + mutation (bloco 15)
├── contexts\AuthContext.tsx ← AuthProvider (named export)
├── hooks
│ ├── useAuth.ts
│ ├── useActivities.ts ← queries + useUploadGpx + useUserActivities + useActivity + useActivityTrack + useDeleteActivity
│ ├── useSocial.ts ← useFeed/useToggleLike/useComments/useFollowUser (invalida activitiesKeys.lists() no follow)
│ ├── useProfile.ts ← useFollowers/useFollowing/useIsFollowing/useUser
│ ├── useStats.ts ← useStatsSummary/useStatsWeekly
│ └── usePhotos.ts ← useActivityPhotos/useUploadPhoto/useDeletePhoto (bloco 15)
├── lib\format.ts
├── pages
│ ├── LoginPage.tsx, RegisterPage.tsx ← default export
│ ├── ActivitiesPage.tsx, UploadPage.tsx ← default export
│ ├── ActivityDetailPage.tsx ← + autor + delete só pro dono + galeria de fotos
│ ├── FeedPage.tsx ← default export
│ └── ProfilePage.tsx ← + username real + atividades + stats (só no próprio)
├── types\api.ts ← espelho dos schemas Pydantic (inclui ActivityPhoto)
├── App.tsx ← rotas
├── main.tsx ← QueryClient + BrowserRouter + AuthProvider
└── index.css
Models existentes (backend)
User

    id (UUID v7), email (unique), username (unique), full_name (nullable)

    hashed_password, weight_kg, height_cm, birth_date

    is_active, created_at, updated_at (todos DateTime(timezone=True))

Activity

    id (UUID v7), user_id (FK users CASCADE)

    activity_type (enum: run/walk/cycle/hike/swim/other)

    title, description, started_at (indexed), finished_at, duration_s

    distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps

    route (Geometry LINESTRING 4326), raw_track_points (JSONB)

    created_at, updated_at

    user = relationship("User", backref="activities", lazy="raise")

    photos = relationship("ActivityPhoto", back_populates="activity", cascade="all, delete-orphan", lazy="raise", order_by="ActivityPhoto.created_at")

ActivityPhoto (bloco 15)

    id (UUID v7)

    activity_id (FK activities CASCADE, indexed)

    url (Text) — URL segura do Cloudinary (secure_url)

    public_id (String 255, unique) — usado pra deletar no Cloudinary

    width (int nullable), height (int nullable)

    created_at (DateTime timezone=True)

    activity = relationship("Activity", back_populates="photos", lazy="raise")

Follow / Like / Comment

    Inalterados desde o Bloco 10.

Endpoints existentes (backend)
Auth & Users

    GET / — metadados

    GET /health — status API + banco

    POST /auth/register — cria (201, 409 se duplicado)

    POST /auth/login — form-urlencoded (username=email), retorna JWT

    GET /auth/me — protegido

    POST /users/{user_id}/follow — 204

    DELETE /users/{user_id}/follow — 204

    GET /users/{user_id}/followers?limit&offset — 200, list[UserPublic]

    GET /users/{user_id}/following?limit&offset — 200, list[UserPublic]

    GET /users/{user_id} — 200, UserPublic (qualquer autenticado)

Activities

    POST /activities — 201 (JSON pré-calculado)

    POST /activities/upload — 201 (multipart, .gpx)

    GET /activities?limit=20&offset=0 — lista próprias

    GET /activities?user_id= — lista de outro (requer follow; 403 caso contrário)

    GET /activities/{id} — dono OU seguidor do dono (404 caso contrário)

    GET /activities/{id}/track — dono OU seguidor do dono

    DELETE /activities/{id} — 204 (só o dono)

    GET /activities/stats/summary?activity_type=

    GET /activities/stats/weekly?weeks=8&activity_type=

    GET /activities/stats/monthly?months=6&activity_type=

    POST /activities/{id}/like — 200, { count, liked_by_me }

    DELETE /activities/{id}/like — 204

    GET /activities/{id}/likes?limit&offset — 200

Comments

    POST /activities/{activity_id}/comments — 201, body { "content": "..." }

    GET /activities/{activity_id}/comments?limit&offset — 200

    DELETE /comments/{comment_id} — 204 (só o autor)

Feed

    GET /feed?limit=20&offset=0 — 200, list[FeedItemResponse]

Photos (bloco 15)

    POST /activities/{activity_id}/photos — 201, multipart file (só o dono)

        Validação: image/jpeg, image/png, image/webp; máx 10 MB

        Upload no Cloudinary em rumo/activities/{activity_id}

    GET /activities/{activity_id}/photos — 200, list[ActivityPhotoResponse]

        Não valida permissão de visualização (dívida consciente)

    DELETE /photos/{photo_id} — 204 (só o dono da atividade)

Frontend — padrões e decisões
web/ como monorepo

    Vercel aponta pra web/ (Root Directory). Render continua em backend/.

    .env.local NUNCA versionado.

    vercel.json dentro de web/.

Cliente HTTP (src/api/client.ts)

    apiFetch<T>(path, options) — única porta pro backend.

    Injeta JWT do localStorage (rumo.token) automaticamente.

    body (objeto) → JSON. rawBody (FormData/URLSearchParams) → passa cru.

    FormData NÃO seta Content-Type manualmente.

    401 limpa token automaticamente.

    Erros viram ApiError(status, detail).

Auth (AuthContext + useAuth + ProtectedRoute)

    Token em localStorage; user em memória.

    Boot do app chama GET /auth/me se houver token.

    register() faz login automático.

    ProtectedRoute redireciona pra /login guardando state.from.

    <AuthProvider> PRECISA envolver <App> no main.tsx.

Rotas atuais (App.tsx)

    /login, /register (públicas)

    /activities (protegida)

    /feed (protegida)

    /upload (protegida)

    /activities/:id (protegida) — detalhe + fotos

    /users/:id (protegida) — perfil

    / → /activities

    * → 404

Convenção de exports (IMPORTANTE)

    Componentes reutilizáveis → named export

        AppHeader, ProtectedRoute, ActivityCard, LikeButton,
        CommentsSection, StatsCards, WeeklyChart, PhotoGallery, PhotoUpload

    Páginas → default export

        ActivitiesPage, UploadPage, LoginPage, RegisterPage,
        ActivityDetailPage, FeedPage, ProfilePage

Query keys (TanStack)

    activitiesKeys: .all, .lists(), .list({...}), .details(), .detail(id), .tracks(), .track(id)

    socialKeys: .feed(limit, offset), .likes(id), .comments(id), .followers(userId), .following(userId)

    statsKeys: .all, .summary(type?), .weekly(weeks, type?)

    photosKeys: .all, .list(activityId)

    ["users", userId] (inline em useUser)

    staleTime: 30s listas/feed/fotos, 5min track/user, 60s stats

    retry: 1, refetchOnWindowFocus: false

Social

    useFeed → ["feed", { limit, offset }], staleTime 30s.

    useToggleLike → otimista com rollback. NÃO invalida feed.

    useFollowUser → invalida ["feed"] + ["followers", id] + ["following", id] + activitiesKeys.lists() (fix pós-15).

    useIsFollowing → busca following do próprio user e checa se alvo está lá.

    Like no card: estado local. Like no detalhe: persistido (GET /likes).

    Clique no coração dentro de <Link>: e.preventDefault() + e.stopPropagation().

Perfil

    ProfilePage usa useUser + useUserActivities + useIsFollowing + useFollowUser.

    Stats só se isSelf === true.

    Filtro por tipo: Tudo/run/walk/cycle/hike/swim.

    403 → CTA "Siga @username...".

    Stats: 4 cards + WeeklyChart.

Fotos

    useActivityPhotos(id) — query, enabled: !!id, staleTime 30s.

    useUploadPhoto / useDeletePhoto — mutations, invalidam photosKeys.list(activityId).

    PhotoUpload — input escondido + botão "+ Adicionar foto"; aceita jpeg/png/webp.

    PhotoGallery — grid aspect-square + object-cover (uniforme), lightbox, ✕ no hover (só dono).

Formatters (src/lib/format.ts)

    formatDistance, formatDuration, formatPace, formatSpeed,
    formatDateTime, formatRelativeDate, formatActivityType, activityEmoji

Tailwind

    Paleta rumo-50 … rumo-900 (laranja). Primária: rumo-500 = #f97316.

    Cor hardcoded no Recharts (#f97316) — se mudar a paleta, atualizar WeeklyChart.tsx.

Tipos (src/types/api.ts)

    ActivityType, UserPublic, UserResponse, Activity, TokenResponse,
    ValidationErrorDetail, TrackResponse, FeedItem, LikeState, LikeList,
    Comment, StatsSummary, StatsPeriod, StatsWeeklyResponse, StatsMonthlyResponse,
    ActivityPhoto

    Interface da atividade se chama Activity (não ActivityResponse).

    Tipos não são gerados do OpenAPI — sincronizados manualmente.

Produção (Render + Neon + Vercel + Cloudinary)
Backend

    API: https://rumo-api-5s0b.onrender.com

    Deploy: git push origin main → Render rebuilda → alembic upgrade head → gunicorn.

    Free tier dorme após 15 min. Primeira request ~30-50s.

    Env vars: DATABASE_URL, ENVIRONMENT=production, DEBUG=false, SECRET_KEY,
    ALGORITHM=HS256, ACCESS_TOKEN_EXPIRE_MINUTES=30, PYTHON_VERSION=3.13.7,
    CLOUDINARY_URL (cloudinary://API_KEY:API_SECRET@bmmu9a3y), ALLOWED_ORIGINS
    json

    ["http://localhost:5173","https://rumo-wheat.vercel.app"]

Cloudinary

    Free tier: 25 créditos/mês (janela móvel de 30 dias).

    Cloud name: bmmu9a3y

    Pasta: rumo/activities/{activity_id}

    CLOUDINARY_URL no Render (sem prefixo CLOUDINARY_URL=, sem aspas).

    SDK lê automaticamente do ambiente.

    Secret nunca no frontend/GitHub/chat.

Frontend

    App: https://rumo-wheat.vercel.app

    Deploy: git push origin main → Vercel rebuilda.

    Root Directory: web/.

    Env var: VITE_API_URL=https://rumo-api-5s0b.onrender.com.

    SPA fallback: web/vercel.json.

Workflow de teste

Testar direto em produção. Build local (npm run build) só pra garantir TS/ESLint limpos antes do push.

Exceção: alembic revision --autogenerate precisa de banco acessível (Docker local ou Neon). upgrade head pode rodar local (Docker) ou no Render (deploy).
Blocos concluídos

    ✅ 1 a 9 (auth, CRUD, GPX, stats backend)

    ✅ 10a Follows / 10b Feed / 10c Likes / 10d Comentários (backend)

    ✅ 11 Deploy Render + Neon

    ✅ 12 Upload GPX backend

    ✅ 13a.0 a 13a.5 (frontend mínimo, deploy Vercel)

    ✅ 13b.1 a 13b.6 (social no frontend)

    ✅ 13b.7 Perfil completo

    ✅ Fix: menu mobile

    ✅ 16 Perfil + stats visuais

    ✅ 15 Fotos de atividade (Cloudinary)

    ✅ Fix pós-15: enquadramento das fotos + invalidação no follow

Blocos pendentes

    ⏳ 17 Notificações — in-app primeiro, push depois. Próximo recomendado.

    ⏳ 12b Upload FIT — opcional, se houver relógio Garmin/Polar.

    ⏳ 14a Mobile Flutter — quando o site no celular não bastar.

    ⏳ 18+ Segments, leaderboards, achievements — Fase 3.

Recomendação de próximo passo

Bloco 17 — Notificações in-app.

Motivo: é o que mais aproxima o Rumo de uma rede social de verdade. Sem notificação, o feed vira via de mão única — o user não sabe que recebeu like/comment/follow.
Escopo (MVP)

Backend:

    Model Notification:

        id (UUID v7)

        recipient_id (FK users, indexed) — quem recebe

        actor_id (FK users) — quem causou

        type (enum: like | comment | follow)

        activity_id (FK activities, nullable) — pra like/comment

        comment_id (FK comments, nullable) — pra comment

        is_read (bool, default False, indexed)

        created_at

    Migração Alembic

    Triggers em like_service, comment_service, follow_service: criar notificação no destinatário (skip se for auto-ação)

    Endpoints:

        GET /notifications?limit&offset — do current_user, ordenado por created_at desc

        GET /notifications/unread-count — { count } (pra badge)

        POST /notifications/{id}/read — marca uma como lida

        POST /notifications/read-all — marca todas como lidas

    Schema NotificationResponse com actor: UserPublic aninhado + activity_preview (title/tipo) opcional

Frontend:

    api/notifications.ts — list/unread-count/read/read-all

    hooks/useNotifications.ts — useNotifications, useUnreadCount, useMarkRead, useMarkAllRead

    components/NotificationBell.tsx — sino no AppHeader com badge de não lidas

    pages/NotificationsPage.tsx — lista com avatar do actor, tipo, atividade, tempo relativo; clique → marca como lida + navega pra atividade/perfil

    Polling useUnreadCount a cada 30s (sem WebSocket no MVP)

    Rota /notifications (protegida)

Não fazer no MVP:

    Push notifications (fica pra depois)

    WebSocket/SSE

    Agrupamento ("X e mais 3 curtiram")

    Preferências de notificação

Pendências técnicas (dívida para limpar)
Backend

    GET /activities/{id}/photos não valida permissão de visualização

    Upload de foto síncrono (bloqueia event loop)

    Delete de foto no Cloudinary silencia exceção (foto órfã possível)

    GET /activities/{id} aceita dono OU seguidor. Decisão em aberto: is_public?

    GET /activities/{id} não aninha author (2 requests no frontend)

    calories NULL no upload GPX

    Sem rate limiting

    Redis não usado

    Sem testes automatizados

    UserResponse expõe email/birth_date

    GET /activities/{id}/comments exige auth

    Upload GPX síncrono

    Cold start do Render free tier

    Stats só do current_user

Frontend

    Thumbnail de foto no ActivityCard (só quando backend expuser cover_photo_url/photo_count)

    useUserActivities fixa limit=20

    Contagem de likes no card do feed é local (não persiste)

    Mapa sem layer switcher (só OSM Standard)

    Tipos em src/types/api.ts não são gerados do OpenAPI

    react-hooks/set-state-in-effect desabilitada no ESLint

    Sem tratamento global de 401 pós-login

    client.ts: as string no VITE_API_URL (cast desnecessário)

    ActivityCard fallback "Atividade" genérico se title/tipo vazios

    Upload sem gestão de rascunho / AbortController

    Erro de rede no upload cai em mutation.error.message cru

    Bundle 598 kB — code splitting com React.lazy planejado

Infra

    vercel.json PRECISA estar em web/

    Preview deploys do Vercel vão precisar de CORS

    Cloudinary free tier: 25 créditos/mês (janela móvel). Se estourar, conta desativada (não cobra)

    Cloudinary: se CLOUDINARY_URL comprometido, rotacionar API Secret

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

    Alembic autogenerate só detecta model se importado em app/models/__init__.py

    Rodar alembic revision --autogenerate duas vezes gera dois arquivos; deletar o errado antes de upgrade head

    Alembic precisa de banco acessível pra autogenerate

    alembic revision cria o arquivo; alembic upgrade head aplica

    venv do backend é D:\Rumo\backend\.venv (com ponto)

    pip install fora da venv cai no Python global — conferir pip show <pkg> → Location

    Pylance reportMissingImports — interpretador errado no VS Code

    cloudinary.uploader.upload é síncrono

    cloudinary.uploader.upload(contents, ...) aceita bytes

    cloudinary.uploader.destroy(public_id) retorna {result: "not found"} sem exception se errado

    Pydantic v2: campo str obrigatório rejeita null

    Model vs banco: editar nullable=True sem migração não altera coluna

    Pydantic Settings + list[str]: parseado via json.loads. Aspas tipográficas quebram

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    Migração com Geometry: import geoalchemy2 + remover op.create_index do GIST

    WKT LINESTRING: ordem (lon lat)

    PostGIS + JSONB redundantes — conferir ST_NPoints == jsonb_array_length

    Dev: PG 16.4 + PostGIS 3.4; Prod: PG 17.11 + PostGIS 3.5

    ST_AsGeoJSON() retorna string JSON

Neon

    PostGIS NÃO vem habilitado — CREATE EXTENSION IF NOT EXISTS postgis;

    Postgres 18 NÃO tem PostGIS no Neon — usar 17

    Usar connection string Direct com asyncpg

    Formato: postgresql+asyncpg://, ssl=require, sem channel_binding

Render

    Blueprint (lê render.yaml)

    Free tier dorme após 15 min

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head &&

    SECRET_KEY com generateValue: true

    CLOUDINARY_URL: colar só o valor, sem prefixo, sem aspas

Cloudinary

    Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

    Placeholders <your_api_key> NÃO são preenchidos automaticamente — montar manualmente

    SDK Python lê CLOUDINARY_URL do ambiente

    secure_url é a URL HTTPS

    public_id é pra deletar

    Free tier: 25 créditos/mês, janela móvel. 1 crédito = 1 GB storage = 1 GB tráfego = 1.000 transformações

    Limite de arquivo: 10 MB por imagem

    API Secret nunca vai pro frontend/GitHub/chat

Vercel

    vercel.json vai no Root Directory (web/)

    SPA fallback obrigatório

    Env vars VITE_* só client-side

Frontend / Vite 8 / React 19 / Tailwind 3

    Vite 8 + TS 6: vite-env.d.ts não existe — types via tsconfig.app.json

    erasableSyntaxOnly: true — proíbe enum, namespace, parameter properties. Usar as const

    noUnusedLocals + noUnusedParameters ativos — TS quebra com import sem uso

    import type { ActivityPhoto } no usePhotos.ts foi removido — tipo é inferido. Se voltar, TS quebra

    Tailwind: fixar em tailwindcss@3

    react-hooks/set-state-in-effect desabilitada

    react-leaflet v5 + React 19: importar "leaflet/dist/leaflet.css" no main.tsx

    MapContainer precisa de height explícita

    <Polyline> espera [[lat, lng], ...] — inverter do GeoJSON [lon, lat]

    React Router v7: pacote react-router-dom

    zod v4: @hookform/resolvers v5+

    Backend espera form-urlencoded no login

    FormData no apiFetch: NÃO setar Content-Type manualmente

    npm run dev vs build: só build roda ESLint + TS

    <AuthProvider> no main.tsx — se faltar, useAuth explode em runtime

    Convenção: componentes = named, páginas = default

    Link dentro de <Link>: HTML inválido. Solução no ActivityCard: <div> wrapper

    NavLink no header pra rota ativa

    Recharts 3.x: react-is peerDependency

    Recharts ResponsiveContainer: pai com height explícita

    Recharts LineChart com 1 ponto: desenha só dot

    <img> com object-cover + h-32 corta fotos — usar aspect-square + object-cover (grid uniforme) ou object-contain (foto inteira)

Ambiente / tooling

    .env nunca commitado. .env.local (web) também não

    Docker Desktop PRECISA estar aberto. docker compose start

    docker compose down -v NUNCA

    Errno 10061 = Postgres local não rodando

    _scratch/ no .gitignore

    PowerShell mostra UTF-8 como Latin-1

    uvicorn não reconhecido: venv não ativada

    PowerShell curl é alias de Invoke-WebRequest. Usar curl.exe ou Invoke-RestMethod

    Ordem de rotas: estáticas antes das dinâmicas

    git commit "nothing to commit" — algo já commitado ou não rastreado

    npm sempre dentro de web/

    VS Code desatualizado: erro ts(2307) com arquivo existente → "TypeScript: Restart TS Server"

Workflow preferido pelo usuário

    Testar direto em produção. Build local só pra garantir TS/ESLint limpos antes do push.

    Sempre seguir a recomendação do chat — não oferecer A/B/C.

    Avisar quando o contexto estiver perto do limite e gerar handoff completo.

    Handoff completo só quando o contexto apertar — não interromper o fluxo.

    Preferência por arquivos completos — quando um arquivo existente muda, entregar o arquivo inteiro.

Convenções

    Comentários/docstrings em português; nomes em inglês.

    REST com prefixos, response_model sempre.

    HTTPException: 401/403/404/409/422/400.

    Commits em português: feat:, fix:, chore:, docs:.

    Blocos incrementais: implementar → testar (em prod) → commitar.

    Explicações didáticas com o "porquê".

    Chat decide o caminho quando há ambiguidade.

Estilo de comunicação preferido

Direto ao ponto, blocos de código prontos para copiar/colar, explicações concisas. Sempre avisar quando estiver perto do limite de contexto.
Usuários de teste
Produção (Neon) — usados agora

    prod@rumo.com / senha12345 (username: produser)

    prod2@rumo.com / senha12345

Local (Docker) — não usados no workflow atual

    teste@rumo.com / senha12345 (username: testuser)

    teste2@rumo.com / senha12345 (username: teste2)

Como retomar (para o próximo chat)

Cola o conteúdo de docs/HANDOFF.md (este bloco) e diga:

    "Retomando o Rumo. Handoff anexo. Bloco 15 + fixes concluídos. Vamos começar o bloco 17 (notificações in-app)."