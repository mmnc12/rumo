Visão do produto (NORTE — ler antes de qualquer decisão)

O Rumo é um app de exercício físico ambicioso, semelhante ao Strava. Não é
um projeto de portfólio nem um CRUD de treinos. O objetivo é produção real,
com usuários reais usando no dia a dia.
O que o Rumo DEVE ter (roadmap ambicioso)

Core (essencial pra ser "Strava-like"):

    ☑

    Auth (register/login/JWT)
    ☑

    CRUD de atividades
    ☑

    Upload de GPX com cálculo automático (distância, pace, elevação)
    □

    Upload de FIT (formato cru dos relógios Garmin/Polar)
    □

    Upload de fotos da atividade (storage S3/Cloudinary/R2)
    □

    Perfil público com stats agregadas (km totais, PRs, gráficos)
    □

    Splits por km (pace e elevação por trecho)
    ☑

    Mapa/visualização da rota no cliente (endpoint dedicado)
    □

    Mapa com layer switcher OSM/Satélite (Fase 2)

Social (o que faz o app engajar):

    ☑

    Follows (seguir/seguidores) — backend
    ☑

    Feed (atividades próprias + de quem segue) — backend
    ☑

    Likes (kudos) — backend
    ☑

    Comentários — backend
    ☑

    Feed/likes/comentários no frontend ← 13b concluído
    □

    Notificações push ("fulano curtiu", "sicrano te seguiu", "novo PR")
    □

    Feed personalizado com filtros (só corrida, só amigos mútuos)
    □

    Compartilhamento externo (card/imagem pra Instagram/WhatsApp)

Diferenciais (o que faz o Strava ser Strava):

    □

    Segments (trechos famosos onde compete por tempo contra outros)
    □

    Leaderboards por segmento
    □

    Achievements/badges ("primeiro 10K", "recorde pessoal")
    □

    Análise de treino (zonas de FC, cadência, comparação semana a semana)

Infra/operacional (obrigatório antes de ir pra produção real):

    □

    Rate limiting
    □

    Cache (Redis — já no docker-compose, não usado ainda)
    □

    Testes automatizados
    □

    Background jobs (processar GPX grandes fora do request)
    □

    Observabilidade (logs estruturados, métricas, tracing)
    □

    Backup do banco

Como usar essa visão

Quando estiver em dúvida sobre uma decisão técnica, perguntar: isso aproxima
o Rumo do Strava ou afasta? Exemplos:

    "Devo expor raw_track_points no ActivityResponse?" → Não, porque
    o cliente (mobile) vai precisar desenhar o mapa — melhor endpoint dedicado
    que retorna só a geometria, pra não pesar a listagem.

    "Devo fazer upload GPX síncrono ou em background?" → No MVP síncrono;
    no futuro, background com fila (Celery/RQ/arq) pra aguentar arquivos grandes.

    "Devo usar SQLite pra simplificar?" → Não. PostGIS é obrigatório (Strava
    é geo-first). Neon já está planejado.

O que o Rumo NÃO é

    ❌ Não é um projeto de portfólio — é um produto de verdade.

    ❌ Não é um "CRUD de exercícios" — é uma rede social de exercícios.

    ❌ Não é um clone literal do Strava — é inspirado, com identidade própria.

Roadmap em fases (vertical slice, não horizontal)

Estratégia: construir features completas atravessando backend + frontend +
mobile, em vez de terminar o backend inteiro antes de começar o frontend.

Por quê:

    "Backend 100%" é miragem — sempre falta algo.

    Frontend/mobile informam o backend sobre o que ainda falta.

    Ver funcionando na tela recarrega a motivação.

    Deploy cedo é barato depois da primeira vez (Render faz redeploy automático).

    Padrão da indústria é vertical slice, não horizontal.

Fase 1 — Deploy + primeira feature visível ✅ CONCLUÍDA

    ✅ Bloco 11: Deploy backend (Render + Neon)

    ✅ Bloco 13a: Frontend mínimo (React/Vercel)

        ✅ 13a.0: Setup Vite + TS + Tailwind + Router + Query + Leaflet

        ✅ 13a.1: Auth (login, registro, ProtectedRoute, AuthContext)

        ✅ 13a.2: Lista de atividades (cards, formatadores, empty state)

        ✅ 13a.3: Upload GPX (drag & drop + multipart + useMutation)

        ✅ 13a.4: Detalhe + mapa (GET /activities/{id}/track + Leaflet)

        ✅ 13a.5: Deploy Vercel + CORS produção + SPA fallback

    ✅ Bloco 13b: Social no frontend ← CONCLUÍDO NESTA SESSÃO

        ✅ 13b.1: Tipos + API + hooks (social.ts, useSocial.ts, types/api.ts)

        ✅ 13b.2: FeedPage + rota /feed + nav no AppHeader + author no card

        ✅ 13b.3: ProfilePage (/users/:id) + follow/unfollow + abas followers/following

        ✅ 13b.4: Like (kudos) no ActivityCard (otimista, local)

        ✅ 13b.5: Comentários + like real (com contagem) na ActivityDetailPage

        ✅ 13b.6 (fix backend): GET /activities/{id} e /track aceitam dono OU seguidor do dono

Resultado: app funcional de ponta a ponta, público, com login, upload de
GPX, lista, mapa, feed social, perfil, follow/unfollow, likes e comentários.
Acessível de qualquer navegador (incluindo celular) via
https://rumo-wheat.vercel.app
Fase 2 — Refinar o que existe (médio prazo)

    Bloco 14a: Mobile mínimo (Flutter) — mesma coisa

    Bloco 15: fotos de atividade

    Bloco 16: perfil público completo + stats visuais

    Bloco 17: notificações (in-app primeiro, push depois)

Fase 3 — Diferenciais do Strava (longo prazo)

    Bloco 18+: segments, achievements, análise de treino

O que NÃO fazer: tentar "terminar o backend antes de tudo". Isso atrasa
meses, mata a motivação, e ignora que o frontend ensina o backend — o 13b
provou isso (o GET /activities/{id} só existia pro dono até o feed expor a
necessidade de abrir pra seguidores).
Stack
Backend

    Python: 3.13.7 + FastAPI + SQLAlchemy 2.0 async + Alembic + GeoAlchemy2

    Banco dev: PostgreSQL 16.4 + PostGIS 3.4 (Docker, postgis/postgis:16-3.4)

    Banco prod: Neon (PostGIS habilitado, projeto rumo, branch production, região AWS US East 2 Ohio, PG 17.11 + PostGIS 3.5)

    Cache: Redis (Docker, ainda não usado)

    Deploy: Render (Blueprint via render.yaml, free tier)

        URL produção: https://rumo-api-5s0b.onrender.com

        Docs: https://rumo-api-5s0b.onrender.com/docs

Frontend

    Vite 8.3.4 + React 19.2.8 + TypeScript 6.0.2

    React Router DOM 7.18.4 (modo SPA, BrowserRouter)

    TanStack Query 5.104.2 (cache/servidor state)

    react-hook-form 7.90.0 + zod 4.6.6 + @hookform/resolvers 5.9.1

    Tailwind CSS 3.4.19 (paleta rumo custom + Inter)

    Leaflet 1.9.4 + react-leaflet 5.0.0 (mapas — OSM Standard)

    ESLint 10 (config flat do Vite v9, react-hooks/set-state-in-effect desabilitada)

    Deploy: Vercel (produção)

        URL produção: https://rumo-wheat.vercel.app

        Root Directory: web/

        Env var: VITE_API_URL=https://rumo-api-5s0b.onrender.com

        SPA fallback: web/vercel.json com rewrite catch-all → /index.html

    Pasta: web/ na raiz do monorepo

Repo / IDE / OS

    Repo: https://github.com/mmnc12/rumo (privado)

    IDE: VS Code (terminal integrado)

    OS: Windows (PowerShell)

    Pacote: npm

Estrutura de pastas (atualizada após 13b)
text

D:\Rumo
├── .gitignore, README.md, docker-compose.yml, render.yaml
├── docs\HANDOFF.md
├── backend
│   ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│   ├── _scratch\ (NÃO versionado)
│   ├── samples\ (não versionado — GPX de teste)
│   ├── alembic\env.py + versions
│   │   └── 19cd7d2f4c3f_full_name_nullable_em_users.py
│   ├── app
│   │   ├── main.py, config.py, database.py
│   │   ├── core\security.py, core\dependencies.py
│   │   ├── models{user,activity,follow,like,comment,init}.py
│   │   ├── schemas{user,activity,stats,like,comment,init}.py
│   │   ├── routers{auth,activities,feed,users,comments,init}.py
│   │   └── services{activity_service,gpx_service,stats_service,follow_service,like_service,feed_service,comment_service,errors,init}.py
│   └── tests\
├── mobile\ (vazio)
└── web
    ├── .env.local (não versionado), .env.example
    ├── .gitignore, eslint.config.js, index.html
    ├── package.json, package-lock.json, postcss.config.js
    ├── tailwind.config.js (paleta rumo)
    ├── tsconfig.json, tsconfig.app.json, tsconfig.node.json
    ├── vercel.json ← SPA fallback (13a.5)
    ├── vite.config.ts
    └── src
        ├── api
        │   ├── client.ts ← apiFetch + ApiError + token helpers
        │   ├── auth.ts ← login/register/getMe
        │   ├── activities.ts ← list/get/delete/uploadGpx/getActivityTrack
        │   └── social.ts ← feed/likes/comments/follows (13b.1)
        ├── components
        │   ├── ProtectedRoute.tsx ← named export
        │   ├── AppHeader.tsx ← named export + nav (Feed / Minhas atividades) + link pro perfil (13b.2)
        │   ├── ActivityCard.tsx ← named export + author opcional + botão de like (13b.2/13b.4)
        │   ├── LikeButton.tsx ← botão de like real com contagem (13b.5)
        │   └── CommentsSection.tsx ← lista + form + delete (13b.5)
        ├── contexts
        │   └── AuthContext.tsx ← AuthProvider (named export)
        ├── hooks
        │   ├── useAuth.ts
        │   ├── useActivities.ts ← queries + useUploadGpx + useActivity + useActivityTrack + useDeleteActivity
        │   ├── useSocial.ts ← useFeed/useToggleLike/useComments/useFollowUser (13b.1)
        │   └── useProfile.ts ← useFollowers/useFollowing/useIsFollowing (13b.3)
        ├── lib
        │   └── format.ts
        ├── pages
        │   ├── LoginPage.tsx ← default export
        │   ├── RegisterPage.tsx ← default export
        │   ├── ActivitiesPage.tsx ← default export
        │   ├── UploadPage.tsx ← default export
        │   ├── ActivityDetailPage.tsx ← default export + like + comentários (13b.5)
        │   ├── FeedPage.tsx ← default export (13b.2)
        │   └── ProfilePage.tsx ← default export (13b.3)
        ├── types
        │   └── api.ts ← espelho dos schemas Pydantic (inclui UserPublic/FeedItem/LikeState/LikeList/Comment)
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

    title, description

    started_at (indexed), finished_at, duration_s

    distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps

    route (Geometry LINESTRING 4326), raw_track_points (JSONB) — formato [[lat, lon, ele, unix_ts], ...]

    created_at, updated_at

    user = relationship("User", backref="activities", lazy="raise")

Follow / Like / Comment

(inalterados desde o Bloco 10)
Endpoints existentes (backend)
Auth & Users

    GET / — metadados

    GET /health — status API + banco

    POST /auth/register — cria usuário (201, 409 se duplicado)

    POST /auth/login — form-urlencoded (username=email), retorna JWT

    GET /auth/me — protegido

    POST /users/{user_id}/follow — 204

    DELETE /users/{user_id}/follow — 204

    GET /users/{user_id}/followers?limit&offset — 200, list[UserPublic]

    GET /users/{user_id}/following?limit&offset — 200, list[UserPublic]

Activities

    POST /activities — 201 (JSON pré-calculado)

    POST /activities/upload — 201 (multipart, .gpx)

    GET /activities?limit=20&offset=0 — lista próprias

    GET /activities/{id} — dono OU seguidor do dono (404 caso contrário) ← mudou no 13b.6

    GET /activities/{id}/track — dono OU seguidor do dono ← mudou no 13b.6 — GeoJSON-like:
    json

    {
      "activity_id": "uuid",
      "type": "LineString",
      "coordinates": [[lon, lat], ...],
      "bbox": [minLon, minLat, maxLon, maxLat],
      "n_points": 2345,
      "simplified": false
    }

    DELETE /activities/{id} — 204 (só o dono — leitura ≠ escrita)

    GET /activities/stats/summary?activity_type=

    GET /activities/stats/weekly?weeks=8&activity_type=

    GET /activities/stats/monthly?months=6&activity_type=

    POST /activities/{id}/like — 200, LikeStateResponse { count, liked_by_me }

    DELETE /activities/{id}/like — 204

    GET /activities/{id}/likes?limit&offset — 200, LikeListResponse { count, liked_by_me, users: UserPublic[] }

Comments

    POST /activities/{activity_id}/comments — 201, body { "content": "..." } (campo é content, não body/text)

    GET /activities/{activity_id}/comments?limit&offset — 200, list[CommentResponse] (array direto, autor aninhado em author)

    DELETE /comments/{comment_id} — 204 (só o autor)

Feed

    GET /feed?limit=20&offset=0 — 200, list[FeedItemResponse] (array direto, não envelopado)

        FeedItemResponse = ActivityResponse + author: UserPublic (validation_alias="user")

Frontend — Padrões e decisões
web/ como monorepo

    Vercel aponta pra web/ (Root Directory). Render continua em backend/.

    .env.local NUNCA versionado.

    vercel.json dentro de web/ (não na raiz do monorepo).

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

    /activities (protegida) — lista próprias

    /feed (protegida) — feed social (13b.2)

    /upload (protegida)

    /activities/:id (protegida) — detalhe (agora abre também pra seguidor do dono)

    /users/:id (protegida) — perfil (13b.3) — usa UUID (não username) porque não há GET /users/{id}

    / → redireciona pra /activities

    * → 404 simples

Convenção de exports (IMPORTANTE — não misturar)

    Componentes reutilizáveis → named export (export function X)

        AppHeader, ProtectedRoute, ActivityCard, LikeButton, CommentsSection

    Páginas → default export (export default function X)

        ActivitiesPage, UploadPage, LoginPage, RegisterPage, ActivityDetailPage, FeedPage, ProfilePage

    Já custou bug de build no 13a.3 (ProtectedRoute importado como default).

Query keys (TanStack)

    activitiesKeys (useActivities.ts): .all, .lists(), .list(params), .details(), .detail(id), .tracks(), .track(id)

    socialKeys (useSocial.ts): .feed(limit, offset), .likes(activityId), .comments(activityId), .followers(userId), .following(userId)

    staleTime: 30s em listas/feed, 5min em track

    retry: 1, refetchOnWindowFocus: false

Social (13b)

    useFeed → ["feed", { limit, offset }], staleTime 30s.

    useToggleLike → otimista com onMutate/onError/onSettled. NÃO invalida o feed no onSettled (o feed não tem contagem de likes — invalidar causaria refetch de 20 atividades a cada clique). Só invalida ["likes", id].

    useFollowUser → invalida ["feed"] + ["followers", id] + ["following", id].

    useIsFollowing (em useProfile.ts) → busca GET /users/{me.id}/following e checa se o alvo está lá. Não existe GET /users/{id}/is-following no backend — a inferência custa 1 request extra.

    useComments/useCreateComment/useDeleteComment → invalidam ["comments", activityId].

    Botão de like no card (ActivityCard): estado local (não busca GET /likes). O coração reflete só o que o usuário fez na sessão. Reload zera.

    Botão de like no detalhe (LikeButton): busca GET /likes de verdade. Contagem real, persiste no reload.

    Clique no coração dentro do <Link>: usa e.preventDefault() + e.stopPropagation() no onClick pra não navegar.

Formatadores (src/lib/format.ts)

formatDistance(m), formatDuration(s), formatPace(sPerKm), formatSpeed(mps), formatDateTime(iso), formatRelativeDate(iso), formatActivityType("run"), activityEmoji("run")
Tailwind

    Paleta custom: rumo-50 … rumo-900 (laranja). Primária: rumo-500 = #f97316.

    Fonte: Inter. Body: bg-gray-50 text-gray-900 antialiased.

Tipos (src/types/api.ts)

    ActivityType, UserPublic, UserResponse, Activity, TokenResponse, ValidationErrorDetail, TrackResponse, FeedItem, LikeState, LikeList, Comment.

    UserPublic tem { id, username, full_name, is_active } (espelha o Pydantic).

    Comment tem { id, activity_id, content, created_at, updated_at, author }.

    Interface da atividade se chama Activity (não ActivityResponse) — espelho local do schema Pydantic. Resolvido quando gerar tipos via OpenAPI (Fase 2).

Produção (Render + Neon + Vercel)
Backend

    API: https://rumo-api-5s0b.onrender.com

    Deploy: git push origin main → Render rebuilda → alembic upgrade head → gunicorn (2 workers uvicorn).

    Free tier dorme após 15 min. Primeira request ~30-50s.

    Env vars no Render: DATABASE_URL, ENVIRONMENT=production, DEBUG=false, SECRET_KEY, ALGORITHM=HS256, ACCESS_TOKEN_EXPIRE_MINUTES=30, PYTHON_VERSION=3.13.7

    ALLOWED_ORIGINS (formato JSON, list[str]):
    json

    ["http://localhost:5173","https://rumo-wheat.vercel.app"]

Frontend

    App: https://rumo-wheat.vercel.app

    Deploy: git push origin main → Vercel rebuilda (~1 min).

    Root Directory: web/

    Env var: VITE_API_URL=https://rumo-api-5s0b.onrender.com

    SPA fallback: web/vercel.json com { "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }

Blocos concluídos

    ✅ 1 a 9 (ver histórico)

    ✅ 10a Follows / 10b Feed / 10c Likes / 10d Comentários

    ✅ 12 Upload GPX backend

    ✅ 11 Deploy Render + Neon

    ✅ 13a.0 a 13a.5 (frontend mínimo completo, deploy Vercel)

    ✅ 13b.1 Tipos + API + hooks (social.ts, useSocial.ts)

    ✅ 13b.2 FeedPage + rota /feed + nav no AppHeader + author no card

    ✅ 13b.3 ProfilePage (/users/:id) + follow/unfollow + abas

    ✅ 13b.4 Like (kudos) no ActivityCard (otimista, local)

    ✅ 13b.5 Comentários + like real (com contagem) na ActivityDetailPage

    ✅ 13b.6 Fix backend: GET /activities/{id} e /track aceitam dono OU seguidor do dono (reusa follow_service.is_following recém-criado)

Blocos pendentes

    ⏳ 13b.7 (recomendado): perfil completo — exige GET /users/{id} no backend

    ⏳ 14a Mobile Flutter mínimo — Fase 1 restante

    ⏳ 12b Upload FIT (opcional, se houver relógio real pra testar)

    ⏳ 15 Fotos de atividade — Fase 2

    ⏳ 16 Perfil público completo + stats visuais — Fase 2 (endpoints /stats/* prontos)

    ⏳ 17 Notificações — Fase 3

    ⏳ 18+ Segments, achievements, análise de treino — Fase 3

Recomendação de ordem (após este handoff)

    13b.7 — Perfil completo (backend + frontend). Adiciona GET /users/{id} e GET /activities?user_id=. Destrava:

        ProfilePage mostra username/full_name do dono (hoje mostra @uuid-curto).

        ProfilePage lista as atividades do usuário (hoje não lista).

        ActivityDetailPage mostra o autor (hoje não mostra, porque GET /activities/{id} não aninha author).

        Abre caminho pro 16 (perfil + stats).

    14a — Flutter (quando o site no celular já não bastar). Precisa do teste manual mobile primeiro pra decidir urgência.

    16 — Perfil + stats visuais (endpoints /stats/* já prontos).

    15 — Fotos (precisa escolher storage: S3/Cloudinary/R2).

    12b — FIT (quando houver relógio pra testar).

Pendências técnicas (dívida para limpar)
Backend

    GET /users/{id} não existe → ProfilePage não mostra username/full_name do dono.

    GET /activities?user_id= não existe → ProfilePage não lista atividades do usuário.

    GET /activities/{id} agora aceita dono OU seguidor. Decisão de produto em aberto: permitir "qualquer autenticado" (atividade pública)? Ou introduzir is_public no model?

    GET /activities/{id} não aninha author — o detalhe não mostra quem fez (só os comentários mostram).

    calories fica NULL no upload GPX — precisa de peso + FC + tipo.

    Sem upload de foto — precisa de storage (S3/Cloudinary/R2).

    Sem rate limiting.

    Redis não usado (está no docker-compose).

    Sem testes automatizados — tests/ vazia.

    UserResponse expõe email e birth_date (só em /auth/me, ok, revisar antes de prod real).

    GET /activities/{id}/comments exige auth — se quiser público, remover Depends(get_current_user).

    Upload GPX síncrono — futuro: fila (arq/Celery/RQ).

    Cold start do Render free tier (~30-50s). Fase 2: subir pro plano pago (~$7/mês).

    SECRET_KEY local e prod diferentes — JWTs não intercambiáveis (correto por design).

Frontend

    ProfilePage mostra @<uuid-truncado> em vez de username (depende de GET /users/{id}).

    ProfilePage não lista atividades do usuário (depende de GET /activities?user_id=).

    Contagem de likes no card do feed é local (não persiste no reload). Só o detalhe tem contagem real.

    Menu mobile: links de nav (Feed, Minhas atividades) somem em telas pequenas (hidden sm:flex). Adicionar hamburger na Fase 2.

    Perfil no mobile: o link do username no AppHeader também é hidden sm:inline. No mobile, só se chega ao perfil via link do feed ou URL direta.

    Mapa sem layer switcher — só OSM Standard. Adicionar toggle Standard/Satélite (Esri World Imagery) na Fase 2.

    Tipos em src/types/api.ts não são gerados do OpenAPI — sincronizados manualmente. Fase 2: openapi-typescript.

    react-hooks/set-state-in-effect desabilitada no eslint.config.js — falso positivo em reidratação. Revisar quando o plugin amadurecer.

    Sem tratamento global de 401 pós-login — hoje apiFetch limpa token mas não redireciona. Fase 2: interceptor global.

    client.ts: as string no VITE_API_URL — cast desnecessário; o if (!API_URL) já faz narrowing.

    ActivityCard mostra title ou cai pra formatActivityType — se ambos vazios, mostrar "Atividade" genérico.

    Lista sem paginação visível — useActivities só busca limit=20. Fase 2.

    Upload sem gestão de "rascunho" — permite navegar pra fora no meio do upload; sem AbortController. Polimento na Fase 2.

    Erro de rede no upload cai em mutation.error.message ("Failed to fetch") — sem tratamento amigável.

    Fallback "sem rota" do ActivityDetailPage implementado mas não testado (não há atividade sem rota no banco).

    useSocial.useToggleLike não usa o LikeState retornado pelo POST (só o otimista). Se quiser, dá pra ramificar (POST usa o body; DELETE confia no otimista).

Infra / deploy

    vercel.json PRECISA estar em web/ (não na raiz do monorepo) porque o Root Directory do Vercel é web/. Colocar na raiz faz o Vercel ignorar silenciosamente.

    Preview deploys do Vercel (cada PR gera URL) vão precisar de CORS. Hoje só Production está em ALLOWED_ORIGINS.

Armadilhas conhecidas (CRÍTICO)
Backend / Python

    bcrypt==4.0.1 obrigatório (4.1+ quebra passlib)

    greenlet==3.1.1 explícito no requirements (Python 3.13)

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso

    include_router sem prefix + @router.post("") = FastAPIError

    ResponseValidationError mascara erro do Pydantic — debugar com TypeAdapter

    selectinload obrigatório quando schema acessa relação em async

    validation_alias no Pydantic pra ORM→JSON com nome diferente (ex: author: UserPublic = Field(validation_alias="user"))

    TYPE_CHECKING pra relationship cross-model sem import circular

    Swagger pré-preenche Form() com "string" literal — validação defensiva no service

    pip install fora da venv cai no Python global

    Ativar a venv antes de rodar uvicorn: .\venv\Scripts\Activate.ps1 (ou python -m uvicorn se o PATH já resolver). O prompt muda pra (venv) PS ...

    Pydantic v2: campo str obrigatório rejeita null com "Field required". Pra aceitar null, precisa str | None = Field(default=None, ...).

    Model vs banco: editar nullable=True no model sem migração NÃO altera a coluna.

    Pydantic Settings + list[str]: o valor da env var é parseado via json.loads. Aspas tipográficas (" ") em vez de retas (" ") quebram com SettingsError: error parsing value for field "ALLOWED_ORIGINS". Fix: digitar as aspas manualmente.

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    Migração com Geometry: adicionar import geoalchemy2 no topo E remover op.create_index do GIST

    WKT LINESTRING: ordem é (lon lat). Ex: LINESTRING(-46.63 -23.55, -46.64 -23.56)

    PostGIS + JSONB redundantes — sempre conferir ST_NPoints(route) == jsonb_array_length(raw_track_points)

    Diferença dev/prod: Docker PG 16.4 + PostGIS 3.4; Neon PG 17.11 + PostGIS 3.5

    ST_AsGeoJSON() retorna string JSON — fazer json.loads() no service. Em alguns casos o driver asyncpg devolve dict direto — defensivamente, checar isinstance(x, dict).

Neon

    PostGIS NÃO vem habilitado por padrão — CREATE EXTENSION IF NOT EXISTS postgis;

    Postgres 18 NÃO tem PostGIS ainda no Neon — usar 17

    Duas connection strings: Pooled (host com -pooler) vs Direct (sem -pooler). Usar Direct com asyncpg.

    Formato: postgresql+asyncpg:// (não postgresql://), ssl=require, sem channel_binding

Render

    Blueprint (lê render.yaml), não Website

    Free tier dorme após 15 min — primeira request ~30-50s

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head && — idempotente

    SECRET_KEY com generateValue: true — diferente da local

Vercel

    vercel.json vai no Root Directory configurado (aqui: web/), NÃO na raiz do monorepo.

    SPA fallback obrigatório: sem rewrite catch-all → /index.html, F5 em rota interna dá 404 do Vercel.

    Se cleanUrls: true, o destino do rewrite é /index (sem .html).

    Env vars VITE_* só são expostas ao código client-side. Prefixo obrigatório.

Frontend / Vite 8 / React 19 / Tailwind 3

    Vite 8 + TS 6: vite-env.d.ts não existe mais — types via tsconfig.app.json → "types": ["vite/client"]

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

    npm run dev vs npm run lint vs npm run build: só build roda o ESLint + TS. Dev server sobe mesmo com erro de linter.

    <AuthProvider> no main.tsx — se faltar, useAuth explode em runtime. Não pega no build.

    Convenção de exports: componentes = named, páginas = default. Não misturar.

    Link dentro de <Link>: HTML inválido. Solução usada no ActivityCard: o <Link> que navega fica dentro de um <div> wrapper; o autor (<Link>) fica fora do <Link> principal (acima). Quando precisa aninhar (like no card), o botão fica dentro do <Link> mas usa e.preventDefault() + e.stopPropagation() no onClick.

    NavLink em vez de Link no header: pra rota ativa ter destaque (isActive no className).

Ambiente / tooling

    .env nunca commitado. .env.local (web) também não.

    Docker Desktop PRECISA estar aberto. docker compose start (não up -d).

    docker compose down -v NUNCA (apaga volume).

    Errno 10061 = Postgres local não está rodando.

    Uvicorn precisa estar em terminal separado.

    _scratch/ no .gitignore.

    PowerShell mostra UTF-8 como Latin-1 — dado íntegro pode parecer corrompido (Ã¡, Ã§, Гўв‚¬В¦). O arquivo no disco provavelmente está OK. Se reescrever pra "corrigir", garanta que o editor salva em UTF-8 (VS Code: canto inferior direito).

    uvicorn não reconhecido no PowerShell: a venv não está ativada. Ativar com .\venv\Scripts\Activate.ps1 (ou python -m uvicorn app.main:app --reload). Se der erro de execution policy, Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass antes.

    PowerShell curl é alias de Invoke-WebRequest. Usar curl.exe ou Invoke-RestMethod.

    Ordem de rotas no router: estáticas antes das dinâmicas (exceto quando o path tem segmentos diferentes — aí não importa).

    git commit "nothing to commit" — algo já foi commitado antes, ou não está rastreado. Conferir git log + git ls-files <path>.

    npm sempre dentro de web/ — a raiz do monorepo não tem package.json.

    VS Code desatualizado: erro ts(2307) (módulo não encontrado) com arquivo existente → Ctrl+Shift+P → "TypeScript: Restart TS Server". O npm run build no terminal resolve se for real.

Convenções

    Comentários/docstrings em português; nomes em inglês.

    REST com prefixos, response_model sempre.

    HTTPException: 401 (auth), 403 (permissão), 404 (not found), 409 (conflito), 422 (Pydantic), 400 (bad request).

    Commits em português, padrão feat:, fix:, chore:, docs:.

    Blocos incrementais: implementar → testar → commitar.

    Usuário prefere explicações didáticas com o "porquê".

    Chat decide o caminho quando há ambiguidade (não fica perguntando "qual prefere?"). Escolher o padrão de mercado, justificar em 1 linha, seguir. Isso agora é regra explícita: sempre seguir a recomendação do chat, sem oferecer A/B/C.

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

Produção (Neon)

    prod@rumo.com / senha12345 (username: produser)

    prod2@rumo.com / senha12345

    (Se prod2 não existir mais, registrar de novo ou criar prod3@rumo.com)

Próximo passo (recomendado)

Bloco 13b.7 — Perfil completo. Backend + frontend, ~1 sessão.

Escopo:

    Backend: adicionar GET /users/{user_id} retornando UserPublic. Sem restrição (qualquer autenticado pode ver o perfil público de outro).

    Backend: adicionar GET /activities?user_id=... (opcional, pra listar atividades de outro). Precisa decidir visibilidade (dono, seguidor, público) — recomendar seguidor do dono, coerente com o GET /activities/{id} do 13b.6.

    Frontend: ProfilePage usa GET /users/{id} → mostra username/full_name de verdade.

    Frontend: ProfilePage lista as atividades do usuário (se o item 2 for feito).

    Frontend: ActivityDetailPage mostra o autor (via GET /users/{user_id} + o user_id que já vem no ActivityResponse).

Depois do 13b.7, o próximo grande passo é o 14a (Flutter) — mas antes vale um teste mobile do site atual pra decidir se o Flutter é urgente ou se pode esperar.

Teste mobile pendente (do handoff anterior, ainda não feito): abrir https://rumo-wheat.vercel.app no celular, validar navegação (o menu some — pendência conhecida), mapa com toque, upload de GPX. O resultado informa a urgência do 14a.