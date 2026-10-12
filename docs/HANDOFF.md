# Rumo — Handoff Atualizado (após Bloco 13a.2)

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
- [ ] Mapa/visualização da rota no cliente (endpoint dedicado)

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
   - ⏳ **13a.3:** Upload GPX (drag & drop + multipart + useMutation) ← PRÓXIMO
   - ⏳ **13a.4:** Detalhe + mapa (precisa de `GET /activities/{id}/track` no backend)
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
│ │ └── 19cd7d2f4c3f_full_name_nullable_em_users.py ← NOVO 13a.1
│ ├── app
│ │ ├── main.py, config.py, database.py
│ │ ├── core\security.py, core\dependencies.py
│ │ ├── models{user,activity,follow,like,comment,init}.py
│ │ ├── schemas{user,activity,stats,like,comment,init}.py
│ │ ├── routers{auth,activities,feed,users,comments,init}.py
│ │ └── services{activity_service,gpx_service,stats_service,follow_service,like_service,feed_service,comment_service,errors,init}.py
│ └── tests
├── mobile\ (vazio)
└── web ← NOVO (Bloco 13a)
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
│ └── activities.ts ← listActivities/getActivity/deleteActivity (13a.2)
├── components
│ ├── ProtectedRoute.tsx ← (13a.1)
│ ├── AppHeader.tsx ← (13a.2)
│ └── ActivityCard.tsx ← (13a.2)
├── contexts
│ └── AuthContext.tsx ← (13a.1)
├── hooks
│ ├── useAuth.ts ← (13a.1)
│ └── useActivities.ts ← (13a.2)
├── lib
│ └── format.ts ← (13a.2)
├── pages
│ ├── LoginPage.tsx ← (13a.1)
│ ├── RegisterPage.tsx ← (13a.1)
│ └── ActivitiesPage.tsx ← (13a.2, substituiu placeholder)
├── types
│ └── api.ts ← espelho dos schemas Pydantic
├── App.tsx ← rotas (13a.1)
├── main.tsx ← QueryClient + BrowserRouter
└── index.css ← Tailwind base


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
- `POST /auth/register` — cria usuário (201, 409 se duplicado). **`full_name` aceita null desde 13a.1**
- `POST /auth/login` — form-urlencoded (username=email), retorna JWT
- `GET /auth/me` — protegido, dados do usuário atual (UserResponse)
- `POST /users/{user_id}/follow` — 204
- `DELETE /users/{user_id}/follow` — 204
- `GET /users/{user_id}/followers?limit&offset`
- `GET /users/{user_id}/following?limit&offset`

### Activities
- `POST /activities` — 201 (JSON pré-calculado)
- `POST /activities/upload` — 201 (multipart, `.gpx`)
- `GET /activities?limit=20&offset=0` — lista próprias (ordenado por `started_at desc`)
- `GET /activities/{id}` — detalhes (só do dono)
- `DELETE /activities/{id}` — 204
- `GET /activities/stats/summary?activity_type=`
- `GET /activities/stats/weekly?weeks=8&activity_type=`
- `GET /activities/stats/monthly?months=6&activity_type=`
- `POST /activities/{id}/like` — 200 `{count, liked_by_me}`
- `DELETE /activities/{id}/like` — 204
- `GET /activities/{id}/likes?limit&offset` — 200 `{count, liked_by_me, users[]}`

**⚠️ Endpoint a CRIAR no 13a.4:** `GET /activities/{id}/track` — retorna GeoJSON
`{activity_id, type: "LineString", coordinates: [[lon,lat,ele], ...], bbox, n_points, simplified: false}`.
Decisão tomada no 13a.0. **Não** expor `route`/`raw_track_points` no `ActivityResponse`.

### Comments
- `POST /activities/{activity_id}/comments` — 201
- `GET /activities/{activity_id}/comments?limit&offset` — 200
- `DELETE /comments/{comment_id}` — 204

### Feed
- `GET /feed?limit=20&offset=0` — atividades próprias + de quem segue

## Frontend — Padrões e decisões (Bloco 13a)

### `web/` como monorepo
- Vercel vai apontar pra `web/` (Root Directory). Render continua em `backend/`.
- **`.env.local` NUNCA versionado** (protegido por `.gitignore` do Vite).

### Cliente HTTP (`src/api/client.ts`)
- `apiFetch<T>(path, options)` — única porta pro backend.
- Injeta JWT do `localStorage` (`rumo.token`) automaticamente.
- `body` (objeto) → JSON. `rawBody` (FormData/URLSearchParams) → passa cru.
- 401 limpa token automaticamente (força novo login).
- Erros viram `ApiError(status, detail)` — `detail` é o `detail` cru do FastAPI.

### Auth (`AuthContext` + `useAuth` + `ProtectedRoute`)
- Token em `localStorage`; user em memória.
- Boot do app chama `GET /auth/me` se houver token (reidrata sessão).
- `register()` faz login automático depois do cadastro.
- `ProtectedRoute` redireciona pra `/login` guardando `state.from`.

### Rotas atuais (`App.tsx`)
- `/login`, `/register` (públicas)
- `/activities` (protegida)
- `/` → redireciona pra `/activities`
- `*` → 404 simples

### Formatadores (`src/lib/format.ts`)
- `formatDistance(m)` → "5,00 km" ou "850 m" (vírgula decimal pt-BR)
- `formatDuration(s)` → "30min", "1h 05min", "45s"
- `formatPace(sPerKm)` → "6:00 /km"
- `formatSpeed(mps)` → "12,4 km/h"
- `formatDateTime(iso)` → "12 out 2026, 15:30"
- `formatRelativeDate(iso)` → "há 2h", "ontem", "há 3 dias"
- `formatActivityType("run")` → "Corrida"
- `activityEmoji("run")` → "🏃"

### TanStack Query (`useActivities`)
- Query keys: `["activities"]`, `["activities","list",params]`, `["activities","detail",id]`
- `staleTime: 30_000` (configurado no `main.tsx`)
- Retry 1, `refetchOnWindowFocus: false`

### Tailwind
- Paleta custom: `rumo-50` … `rumo-900` (laranja). Primária: `rumo-500` = `#f97316`.
- Fonte: Inter (Google Fonts).
- Body: `bg-gray-50 text-gray-900 antialiased`.

### ESLint
- Flat config do Vite v9.
- **Regra `react-hooks/set-state-in-effect` desabilitada** (falso positivo em reidratação de sessão — ver dívida técnica).

## Produção (Render + Neon)

- **API:** `https://rumo-api-5s0b.onrender.com`
- **Deploy:** `git push origin main` → Render rebuilda → aplica `alembic upgrade head` → sobe gunicorn (2 workers uvicorn).
- **Free tier dorme após 15 min** sem tráfego. Primeira request ~30-50s.
- **Env vars no Render:** `DATABASE_URL`, `ENVIRONMENT=production`, `DEBUG=false`, `SECRET_KEY`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `ALLOWED_ORIGINS=["http://localhost:5173"]`, `PYTHON_VERSION=3.13.7`
- **Deploy da migração 19cd7d2f4c3f confirmado** no log do Render em 12/10/2026 15:19 UTC.

## Blocos concluídos

- ✅ 1 a 9 (ver histórico)
- ✅ 10a Follows / 10b Feed / 10c Likes / 10d Comentários
- ✅ 12 Upload GPX backend
- ✅ 11 Deploy Render + Neon (Blueprint, CORS, gunicorn)
- ✅ 13a.0 Setup Vite+TS+Tailwind+Router+Query+Leaflet
- ✅ 13a.1 Auth (login/registro/ProtectedRoute/AuthContext) + fix `full_name` nullable (schema + model + migração `19cd7d2f4c3f`)
- ✅ 13a.2 Lista de atividades (cards, formatadores, empty state)

## Blocos pendentes

- ⏳ **13a.3 Upload GPX no frontend** ← PRÓXIMO
  - `src/api/activities.ts`: adicionar `uploadGpx(file, meta?)` (multipart)
  - `src/pages/UploadPage.tsx` (drag & drop + input file + progress + redirect)
  - `src/App.tsx`: adicionar rota `/upload`
  - `useMutation` invalidando `activitiesKeys.all` após sucesso
- ⏳ **13a.4 Detalhe + mapa**
  - **Backend:** `GET /activities/{id}/track` (GeoJSON, ver decisão no 13a.0)
  - **Frontend:** `src/pages/ActivityDetailPage.tsx`, `<MapContainer>` + `<Polyline>`, cards de métricas
- ⏳ **13a.5 Deploy Vercel + CORS produção**
  - Vercel Root Directory = `web/`
  - `VITE_API_URL=https://rumo-api-5s0b.onrender.com` nas env vars do Vercel
  - **Atualizar `ALLOWED_ORIGINS` no Render** com URL real da Vercel
- ⏳ 14a Mobile Flutter mínimo — Fase 1
- ⏳ 12b Upload FIT (opcional)
- ⏳ 13b/14b Feed/likes/comentários no frontend/mobile — Fase 2
- ⏳ 15 Fotos de atividade — Fase 2
- ⏳ 16 Perfil público + stats visuais — Fase 2
- ⏳ 17+ Segments, achievements, notificações, análise de treino — Fase 3

## Pendências técnicas (dívida para limpar)

### Backend
1. `calories` fica NULL no upload GPX — cálculo precisa de peso + FC + tipo.
2. Sem upload de foto de atividade — precisa de storage (S3/Cloudinary/R2).
3. Sem rate limiting.
4. Redis não usado (está no docker-compose).
5. Sem testes automatizados — `tests/` vazia.
6. `UserResponse` expõe `email` e `birth_date` (só em `/auth/me`, ok, mas revisar antes de prod real).
7. `GET /activities/{id}/comments` exige auth — se quiser público, remover `Depends(get_current_user)`.
8. **Sem `/activities/{id}/track`** — criar no 13a.4 (GeoJSON, ver decisão).
9. Upload GPX síncrono — futuro: fila (arq/Celery/RQ).
10. **Cold start do Render free tier** (~30-50s). Fase 2: subir pro plano pago (~$7/mês).
11. **`ALLOWED_ORIGINS` no Render aponta só pra `localhost:5173`** — atualizar no 13a.5 com URL da Vercel.
12. `SECRET_KEY` local e de prod diferentes — JWTs não intercambiáveis (correto por design).

### Frontend
13. **Tipos em `src/types/api.ts` não são gerados do OpenAPI** — sincronizados manualmente. Fase 2: `openapi-typescript`.
14. **`react-hooks/set-state-in-effect` desabilitada** no `eslint.config.js` — falso positivo em reidratação de sessão. Revisar quando o plugin amadurecer.
15. **Sem tratamento global de 401 pós-login** — hoje `apiFetch` limpa token mas não redireciona. Se uma request autenticada der 401 (token expirou), o usuário fica "logado" na UI até próximo `refetch`. Fase 2: interceptor global que força `logout()`.
16. **`ActivityCard` mostra `title` ou cai pro `formatActivityType`** — se ambos ficarem vazios, mostrar "Atividade" genérico.
17. **Lista sem paginação visível** — `useActivities` só busca `limit=20`, sem infinite scroll/botão "carregar mais". Fase 2.
18. **Sem `AppHeader` link pra perfil/feed** — só "Rumo" + logout. Adicionar no 13b.

## Armadilhas conhecidas (CRÍTICO)

### Backend / Python
- `bcrypt==4.0.1` obrigatório (4.1+ quebra passlib)
- `greenlet==3.1.1` explícito no requirements (Python 3.13)
- `uuid.uuid7` NÃO existe no Python 3.13 — usar `from uuid6 import uuid7`
- `DateTime` sem `timezone=True` — bug silencioso
- `include_router` sem prefix + `@router.post("")` = FastAPIError
- `ResponseValidationError` mascara erro do Pydantic — debugar com `TypeAdapter`
- `selectinload` obrigatório quando schema acessa relação em async
- `validation_alias` no Pydantic pra ORM→JSON com nome diferente
- `TYPE_CHECKING` pra relationship cross-model sem import circular
- **Swagger pré-preenche `Form()` com `"string"` literal** — validação defensiva no service
- **`pip install` fora da venv cai no Python global**
- **Pydantic v2:** campo `str` obrigatório rejeita `null` com `Field required` mesmo quando o frontend manda `full_name: null` explícito. Pra aceitar null, precisa `str | None = Field(default=None, ...)`. **Foi exatamente o bug do 13a.1.**
- **Model vs banco:** editar `nullable=True` no model sem gerar migração **NÃO** altera a coluna. Sempre rodar `alembic revision --autogenerate` + `alembic upgrade head`.

### Banco / PostGIS
- Alembic + PostGIS: filtro `include_object` no `env.py`
- Migração com `Geometry`: adicionar `import geoalchemy2` no topo E remover `op.create_index` do GIST
- WKT LINESTRING: ordem é `(lon lat)`. Ex: `LINESTRING(-46.63 -23.55, -46.64 -23.56)`
- PostGIS + JSONB redundantes — sempre conferir `ST_NPoints(route) == jsonb_array_length(raw_track_points)`
- Diferença dev/prod: Docker PG 16.4 + PostGIS 3.4; Neon PG 17.11 + PostGIS 3.5

### Neon
- PostGIS NÃO vem habilitado por padrão — `CREATE EXTENSION IF NOT EXISTS postgis;`
- Postgres 18 NÃO tem PostGIS ainda no Neon — usar 17
- Duas connection strings: Pooled (host com `-pooler`) vs Direct (sem `-pooler`). **Usar Direct com asyncpg**
- Formato: `postgresql+asyncpg://` (não `postgresql://`), `ssl=require`, sem `channel_binding`

### Render
- Blueprint (lê `render.yaml`), não Website
- Free tier dorme após 15 min — primeira request ~30-50s
- `rootDir: backend` no `render.yaml`
- `startCommand` com `alembic upgrade head &&` — idempotente
- `SECRET_KEY` com `generateValue: true` — diferente da local

### Frontend / Vite 8 / React 19 / Tailwind 3
- **Vite 8 + TS 6:** `vite-env.d.ts` **não existe mais** — types do Vite vêm via `tsconfig.app.json` → `"types": ["vite/client"]`
- **`erasableSyntaxOnly: true`** no `tsconfig.app.json` (Vite 8) — **proíbe `enum`, `namespace`, parameter properties em construtor**. Usar `as const` pra constantes tipo enum.
- **`noUnusedLocals` + `noUnusedParameters`** ativos — TS quebra o build com variável/import sem uso.
- **Tailwind: fixar em `tailwindcss@3`** — a v4 mudou o CLI (não tem `npx tailwindcss init -p`). Migração fica pra Fase 3.
- **`react-hooks/set-state-in-effect`** (novo no `eslint-plugin-react-hooks` v7+) dispara falso positivo em `setState` dentro de `useEffect`. Desabilitado no `eslint.config.js`.
- **`react-leaflet` v5 + React 19:** compatível, mas importar `"leaflet/dist/leaflet.css"` no `main.tsx` é obrigatório (senão tiles desalinhados).
- **React Router v7:** pacote continua `react-router-dom`, API compatível com v6. Sem breaking change relevante.
- **zod v4:** API compatível com v3 pro que usamos, mas `@hookform/resolvers` precisa ser v5+.
- **Backend espera form-urlencoded no login** (`OAuth2PasswordRequestForm`), não JSON. Montar manualmente com `URLSearchParams`.
- **FormData no `apiFetch`:** setar `Content-Type: multipart/form-data` manualmente **quebra** (falta o `boundary`). Deixar o browser setar.
- **`npm run dev` vs `npm run lint` vs `npm run build`:** só `build` roda o ESLint + TS. Dev server sobe mesmo com erro de linter.

### Ambiente / tooling
- `.env` nunca commitado. `.env.local` (web) também não.
- Docker Desktop PRECISA estar aberto. `docker compose start` (não `up -d`).
- `docker compose down -v` NUNCA (apaga volume).
- `Errno 10061` = Postgres local não está rodando.
- Uvicorn precisa estar em terminal separado.
- `_scratch/` no `.gitignore`.
- PowerShell mostra UTF-8 como Latin-1 — dado íntegro no banco pode parecer corrompido no terminal.
- **PowerShell `curl` é alias de `Invoke-WebRequest`.** Pra curl de verdade: `curl.exe`. Pra JSON no PowerShell, preferir `Invoke-RestMethod`.
- **Ordem de rotas no router:** estáticas antes das dinâmicas.
- **Quando `git commit` diz `nothing to commit, working tree clean`** — algo já foi commitado antes, ou os arquivos não estão rastreados. Conferir com `git log` + `git ls-files <path>`.

## Convenções

- Comentários/docstrings em **português**; nomes em **inglês**.
- REST com prefixos, `response_model` sempre.
- HTTPException: 401 (auth), 403 (permissão), 404 (not found), 409 (conflito), 422 (Pydantic), 400 (bad request).
- Commits em português, padrão `feat:`, `fix:`, `chore:`, `docs:`.
- Blocos incrementais: implementar → testar → commitar.
- Usuário prefere **explicações didáticas com o "porquê"**.
- Sempre avisar quando estiver perto do limite de contexto e gerar handoff.

## Estilo de comunicação preferido

Direto ao ponto, blocos de código prontos para copiar/colar, explicações concisas. Sempre avisar quando estiver perto do limite de contexto.

## Usuários de teste

### Local (Docker)
- `teste@rumo.com` / `senha12345` (id: `01a0f49c-8e6d-7506-a1c1-1c8c72c50523`, username: `testuser`)
- `teste2@rumo.com` / `senha12345` (id: `01a0f9c4-0552-721d-90ea-e7b0ff9af1e1`, username: `teste2`)
- User1 segue User2
- User2 tem 2 atividades "Corrida do user2" (7000m, 2400s, 450 kcal)
- User1 tem 1 atividade "Corrida matinal" (5000m, 1800s, 320 kcal)
- Activity do user2 para testes de comments: `01a0f9d8-8431-7d78-a943-bc832533454c`
- GPX de teste: `backend/samples/sample_run.gpx` (2345 pontos, ~7.3km caminhada)
- **Usuários criados no 13a.1:** `novo1@rumo.com`, `novo2@rumo.com` (via curl, sem full_name)

### Produção (Neon)
- `prod@rumo.com` / `senha12345` (username: `produser`)
- `prod2@rumo.com` / `senha12345` (criado durante smoke test do 13a.1)

## Próximo passo (13a.3 — Upload GPX no frontend)

**Objetivo:** tela `/upload` com drag & drop, chama `POST /activities/upload`, invalida cache da lista, redireciona pro detalhe (ou pra lista).

**Arquivos a criar/modificar:**
1. `web/src/api/activities.ts` — adicionar `uploadGpx(file: File, meta?)`
2. `web/src/hooks/useActivities.ts` — adicionar `useUploadGpx()` (useMutation)
3. `web/src/pages/UploadPage.tsx` — tela com drag & drop
4. `web/src/App.tsx` — rota `/upload` protegida

**Backend já está pronto** — só consumir.

**Ponto de atenção:** o backend espera multipart com `file` (obrigatório) + `title`/`activity_type`/`description` (opcionais). O `apiFetch` já tem suporte a `rawBody` (FormData).