Produção funcionando (Render + Vercel + Neon + Cloudinary). Cinco blocos concluídos e testados em prod nesta sessão:

    17 BACKEND (notificações)

    17 FRONTEND (sino + página + polling 30s)

    17b BACKEND (cover_photo_url + photo_count denormalizados, migração 517496af416f aplicada no Neon)

    17b FRONTEND (thumbnail lateral + badge no ActivityCard)

    Busca de usuários (GET /users/search + página /search + input no header + item no drawer)

Todos commitados e pushados. Render e Vercel no head. npm run build limpo (chunk principal 367.26 kB / gzip 112.30 kB, SearchPage em chunk próprio 2.57 kB, @tanstack/react-query compartilhado em client-HjIwgQok.js).
O que foi feito neste chat
1. Bloco 17 FRONTEND — Notificações ✅ CONCLUÍDO E TESTADO EM PROD

(Do handoff anterior — resumo: types/api.ts com tipos de notificação, api/notifications.ts, hooks/useNotifications.ts com polling 30s, NotificationBell.tsx, NotificationsPage.tsx, rota protegida em App.tsx com lazy + Suspense, sino no desktop + drawer mobile. Code splitting via rolldownOptions.output.codeSplitting.groups — leaflet e recharts isolados. Testado com prod@rumo.com / prod2@rumo.com.)
2. Bloco 17b BACKEND — cover_photo_url + photo_count ✅ CONCLUÍDO

Decisão arquitetural: Opção A — denormalização no model Activity (não subquery, não endpoint separado). Justificativa: Strava-faithful, query de feed barata, from_attributes=True mantido nos schemas, fonte da verdade continua em activity_photos mas só photo_service escreve os denormalizados.

Arquivos:

    backend/app/models/activity.py — cover_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True), photo_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0") + CheckConstraint("photo_count >= 0", name="ck_photo_count_non_negative")

    backend/app/schemas/activity.py — cover_photo_url: str | None e photo_count: int em ActivityResponse (herda em FeedItemResponse)

    backend/app/services/photo_service.py — upload: se photo_count == 0 seta cover_photo_url = photo.url, sempre incrementa. Delete: await db.flush() no DELETE, depois _recalc_cover_and_count(db, activity) (SELECT ordenado por created_at ASC, seta photo_count = len(photos) e cover_photo_url = photos[0].url if photos else None)

    backend/alembic/versions/517496af416f_add_cover_photo_url_and_photo_count_to.py — ADD COLUMN + backfill (UPDATE ... FROM (subquery com ARRAY_AGG(url ORDER BY created_at ASC))[1]) + CHECK CONSTRAINT

    activity_service.py e feed_service.py — inalterados

Migração aplicada: alembic current → 517496af416f (head). Backfill rodou. Commit + push feitos.
3. Bloco 17b FRONTEND — Thumbnail no ActivityCard ✅ CONCLUÍDO E TESTADO EM PROD

Arquivos:

    web/src/types/api.ts — cover_photo_url: string | null e photo_count: number em Activity (herda em FeedItem)

    web/src/components/ActivityCard.tsx — thumbnail lateral h-24 w-24 shrink-0 overflow-hidden rounded-lg object-cover à esquerda, <img loading="lazy" decoding="async"> dentro do <Link> existente (sem <Link> aninhado), badge com photo_count total sobreposto no canto inferior direito quando > 1, fallback = layout atual sem placeholder

Testado em prod nos 3 contextos (/feed, /activities, /users/{id}): foto → thumb, sem foto → layout atual, 2+ fotos → badge, clique → /activities/{id}, LikeButton preservado.
4. Busca de usuários — backend ✅ CONCLUÍDO E TESTADO EM PROD

Arquivos:

    backend/app/services/user_service.py (novo) — search_users(db, q, current_user_id, limit) com ILIKE em username e full_name via or_, User.is_active.is_(True), User.id != current_user_id, ordenação por case de relevância (prefixo username → prefixo full_name → contém), desempate por username ASC. ServiceError(400) se termo < 2 chars.

    backend/app/api/routes/users.py — GET /search antes de GET /{user_id} (armadilha: senão FastAPI tenta UUID("search") → 422). q: Query(min_length=2, max_length=100), limit: Query(default=20, ge=1, le=50), response_model=list[UserPublic], Depends(get_current_user).

    backend/app/schemas/user.py — inalterado (reusa UserPublic com from_attributes=True, mesmo padrão de list_followers/list_following).

Sem índice pg_trgm — decisão consciente: full scan OK até ~5k usuários; dívida registrada. Testado em /docs em prod: q=prod logado como produser → prod2; q=PROD → case-insensitive; q=p → 422; q=zzz → []; sem token → 401.
5. Busca de usuários — frontend ✅ CONCLUÍDO E TESTADO EM PROD

Arquivos novos:

    web/src/hooks/useDebounce.ts — useDebounce<T>(value, delay=300)

    web/src/hooks/useUserSearch.ts — React Query, queryKey: ["users", "search", trimmed], enabled: trimmed.length >= 2, staleTime: 30_000, encodeURIComponent

    web/src/pages/SearchPage.tsx — default export, input controlado + debounce 300ms, lê q da URL via useSearchParams (deep-linkable: /search?q=prod inicializa input), sincroniza debounced de volta pra URL com replace: true, estados separados (tooShort / isPending / isError / empty / results), avatar circular com inicial do username, link inteiro → /users/{id}

Arquivos modificados:

    web/src/App.tsx — rota /search protegida, SearchPage em React.lazy

    web/src/components/AppHeader.tsx — <form role="search" onSubmit={goToSearch}> com input type="search" no desktop (uncontrolled, só navega), useNavigate pra /search?q=... ou /search; DrawerLink to="/search" no drawer mobile após "Minhas atividades"

Testado em prod: busca funciona nos 2 sentidos (prod→prod2, prod2→prod), 2 chars mínimo, q=PROD case-insensitive, click → /users/{id}, header Enter → /search?q=... com input preenchido, refresh mantém, drawer mobile navega, deslogado → /login.
⏳ PRÓXIMO PASSO: Bloco — Rate limiting (slowapi)

Contexto do porquê (para o próximo chat): superfície de ataque aumentou com a busca (GET /users/search?q=aa = full scan ILIKE em username + full_name). Free tier frágil: Render dorme, Neon tem limite de conexão, Cloudinary 25 créditos/mês. Um scraper derruba o app pros usuários reais.
Estado atual relevante (que o próximo chat precisa saber)

slowapi NÃO está instalado. backend/requirements.txt atual tem FastAPI 0.115.6, Starlette implícito (compatível com slowapi ≥0.1.9), sem slowapi. Adicionar do zero: pip install slowapi + linha no requirements.txt.

backend/app/main.py atual (completo no anexo do usuário):

    app = FastAPI(...) module-level com lifespan

    CORS middleware

    include_router de auth, activities (/activities), users (/users), feed (/feed), comments, photos, notifications

    Rotas GET / e GET /health

    Não tem app.state.limiter nem exception_handler de 429

backend/app/core/dependencies.py atual (completo no anexo):

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    get_current_user(token, db) -> User — valida JWT, busca User, checa is_active, retorna 403 se inativo

    Não tem Request no signature — slowapi exige que o endpoint decorado tenha request: Request no signature (não no dep), então adicionar @limiter.limit(...) em endpoints existentes exige adicionar request: Request como primeiro param em cada endpoint decorado. Isso é invasivo em auth.py, users.py (só POST /activities e POST /photos são críticos), então mapear antes de sair editando.

Escopo proposto

Backend:

    pip install slowapi + slowapi no requirements.txt

    backend/app/core/rate_limit.py (novo) — Limiter(key_func=get_remote_address), handler 429 retornando JSON {"detail": "Muitas requisições. Tente novamente em instantes."}

    main.py — app.state.limiter = limiter, app.add_exception_handler(RateLimitExceeded, handler), app.add_middleware(SlowAPIMiddleware) (ou usar SlowAPIMiddleware se o handler for exception-based — conferir doc do slowapi na hora)

    Decorators cirúrgicos (não globais — rate limit global pune usuário legítimo scrollando feed):

        POST /auth/login — 5/minute (brute force)

        POST /auth/register — 3/hour por IP (spam)

        GET /users/search — 20/minute (scraper)

        POST /activities (upload GPX) — 10/hour (síncrono pesado)

        POST /activities/{id}/photos — 20/hour

        Resto: sem limit neste bloco

    Cada endpoint decorado ganha request: Request no signature (não quebra chamadas do frontend — request é injetado pelo FastAPI)

Frontend: nada a fazer — apiFetch já recebe 429, React Query mostra erro. Só testar que a UX de erro é decente (não travar).

Testar em prod: martelar /users/search com curl.exe até 429, confirmar /feed não afetado, confirmar reset após janela.

Estimativa: ~40min backend + ~15min teste.
Ordem de recomendação pós-rate-limiting

    Rate limiting (slowapi) ← próximo

    is_public no GET /activities/{id} (decisão de produto pendente)

    Paginação em useUserActivities / feed

    Upload de foto assíncrono (BackgroundTasks)

    GET /activities/{id} aninhar author (economiza 2 requests)

    Busca de atividades (feature nova, expande /search pra atividades)

    Bloco 12b: Upload FIT (opcional, se tiver relógio)

    Bloco 14a: Mobile Flutter mínimo

Dívidas conhecidas (atualizadas)
Backend

    GET /activities/{id}/photos não valida permissão de visualização

    Upload de foto síncrono (bloqueia event loop ~1–3s)

    Delete de foto no Cloudinary silencia exceção (foto órfã possível)

    GET /activities/{id} aceita dono OU seguidor. Decisão em aberto: is_public?

    GET /activities/{id} não aninha author (2 requests no frontend)

    calories NULL no upload GPX

    Sem rate limiting ← próximo bloco

    Redis não usado

    Sem testes automatizados

    UserResponse expõe email/birth_date

    GET /activities/{id}/comments exige auth

    Upload GPX síncrono

    Cold start do Render free tier

    Stats só do current_user

    Sem índice pg_trgm pra busca (nova — full scan OK até ~5k users; criar GIN gin_trgm_ops quando crescer)

Frontend

    useUserActivities fixa limit=20 — sem paginação

    Contagem de likes no card do feed é local (não persiste)

    Mapa sem layer switcher

    Tipos em src/types/api.ts não gerados do OpenAPI

    react-hooks/set-state-in-effect desabilitada no ESLint

    Sem tratamento global de 401 pós-login

    client.ts: as string no VITE_API_URL (cast desnecessário)

    ActivityCard fallback "Atividade" genérico

    Upload sem rascunho / AbortController

    ~~Sem busca de usuários~~ ← RESOLVIDO

    Bundle: resolvido via code splitting (leaflet + recharts separados)

    SearchPage sincroniza q na URL com replace: true — se o histórico precisar ser preservado (ex: voltar pra busca anterior), revisar

Infra

    Docker Desktop precisa estar aberto pra docker compose local

    .env local aponta pra Neon (prod) ou Docker — conferir antes de qualquer alembic comando pra não aplicar migração no banco errado

    Cloudinary free tier: 25 créditos/mês

    vercel.json precisa estar em web/

    Slowapi não instalado no venv (verificar pip show slowapi antes de commitar — se o Render falhar com ImportError, é porque o requirements.txt não foi pushado junto)

Roadmap atualizado

Fase 1 — Deploy + primeira feature ✅

Fase 2 — Refinar o que existe (em andamento):

    ✅ Bloco 16: Perfil + stats visuais

    ✅ Bloco 15: Fotos (Cloudinary)

    ✅ Fixes pós-15

    ✅ Bloco 17 BACKEND: Notificações

    ✅ Bloco 17 FRONTEND: Notificações

    ✅ Bloco 17b BACKEND: cover_photo_url + photo_count

    ✅ Bloco 17b FRONTEND: thumbnail no ActivityCard

    ✅ Busca de usuários (backend + frontend)

    ⏳ Rate limiting (slowapi) ← PRÓXIMO

    ⏳ is_public no GET /activities/{id}

    ⏳ Paginação em feed/activities

    ⏳ Upload de foto assíncrono

    ⏳ Bloco 12b: Upload FIT (opcional)

    ⏳ Bloco 14a: Mobile Flutter mínimo

Fase 3 — Diferenciais Strava (segments, leaderboards, achievements) — longo prazo
Preferências do usuário (CRÍTICO — seguir sempre)

    Sempre seguir a recomendação do chat — não oferecer A/B/C. O usuário confia na recomendação e quer ser direcionado.

    Avisar quando o contexto estiver perto do limite e gerar handoff completo.

    Handoff completo só quando o contexto apertar — não interromper o fluxo.

    Preferência por arquivos completos — quando um arquivo existente muda, entregar o arquivo inteiro (não diff, não "adicione estas linhas").

    Explicações didáticas com o "porquê" — concisas mas com justificativa técnica.

    Comentários/docstrings em português; nomes em inglês.

    Commits em português: feat:, fix:, chore:, docs:.

    Testar direto em produção. Build local só pra garantir TS/ESLint limpos antes do push.

    Blocos incrementais: implementar → testar (em prod) → commitar.

Armadilhas conhecidas (CRÍTICO — não repetir)
Backend / Python

    bcrypt==4.0.1 obrigatório (4.1+ quebra passlib)

    greenlet==3.1.1 explícito (Python 3.13)

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso

    selectinload obrigatório quando schema acessa relação em async

    Alembic autogenerate só detecta model se importado em app/models/__init__.py

    Rodar alembic revision --autogenerate duas vezes gera dois arquivos; deletar o errado

    alembic revision cria o arquivo; alembic upgrade head aplica

    venv é D:\Rumo\backend\.venv (com ponto): .\.venv\Scripts\Activate.ps1

    pip install fora da venv cai no Python global

    cloudinary.uploader.upload é síncrono; aceita bytes; destroy(public_id) retorna {result: "not found"} sem exception se errado

    Pydantic v2: campo str obrigatório rejeita null

    Model vs banco: editar nullable=True sem migração não altera coluna

    include_router COM prefix + router que já declara prefix = /prefix/prefix (aconteceu no bloco 17)

    IntegrityError no flush → rollback → só então criar notificação (padrão bloco 17: flush antes de create_notification)

    Rotas estáticas ANTES das dinâmicas — /users/search antes de /users/{user_id} (aconteceu neste bloco: sem isso, FastAPI tenta UUID("search") → 422)

    slowapi exige request: Request no signature do endpoint decorado — não no dep. Adicionar em cada endpoint com @limiter.limit, não em dependencies.py. Request é injetado pelo FastAPI, não quebra frontend.

    slowapi + FastAPI module-level app: app.state.limiter = limiter + app.add_exception_handler(RateLimitExceeded, handler) após criar o app. Se usar SlowAPIMiddleware, app.add_middleware(SlowAPIMiddleware).

    Não aplicar rate limit global — punir usuário legítimo scrollando feed é pior que a ameaça. Cirúrgico por endpoint.

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    WKT LINESTRING: ordem (lon lat)

    Dev: PG 16.4 + PostGIS 3.4; Prod: PG 17.11 + PostGIS 3.5

    Neon: PostGIS NÃO vem habilitado (CREATE EXTENSION IF NOT EXISTS postgis;); Postgres 18 NÃO tem PostGIS no Neon (usar 17)

    Neon: connection string Direct com asyncpg, ssl=require, sem channel_binding

    ILIKE com %termo% NÃO usa índice B-tree — full scan é o que roda hoje em /users/search. Aceitável até ~5k users; depois, índice GIN com gin_trgm_ops.

Render

    Free tier dorme após 15 min

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head &&

    CLOUDINARY_URL: colar só o valor, sem prefixo, sem aspas

    Deploy Failed com ImportError: conferir git ls-files + nome exato do símbolo

    Deploy pode ficar velho se requirements.txt não for pushado junto — slowapi novo: adicionar ao requirements.txt E pushar, senão Render falha no pip install no deploy.

Cloudinary

    Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

    CLOUDINARY_URL no Render: só o valor

    SDK Python lê do ambiente

    secure_url é a URL HTTPS; public_id é pra deletar

    URL original sem transform — thumb do ActivityCard usa secure_url direto (cada transformação consome crédito do free tier: 25/mês)

Vercel

    vercel.json em web/ (Root Directory)

    SPA fallback obrigatório

    Env vars VITE_* só client-side

Frontend / Vite 8 / React 19 / Tailwind 3

    Vite 8 usa Rolldown — build.manualChunks objeto quebrou TS (ManualChunksFunction não aceita chaves); usar build.rolldownOptions.output.codeSplitting.groups com { name, test: /regex/ }

    rollupOptions ainda funciona como alias/compat, mas rolldownOptions é o nome novo — preferir rolldownOptions

    Vite 8 + TS 6: vite-env.d.ts não existe — types via tsconfig.app.json

    erasableSyntaxOnly: true — proíbe enum, namespace, parameter properties

    noUnusedLocals + noUnusedParameters ativos — TS quebra com import sem uso

    Tailwind: fixar em tailwindcss@3

    react-leaflet v5 + React 19: importar "leaflet/dist/leaflet.css" no main.tsx

    MapContainer precisa de height explícita

    <Polyline> espera [[lat, lng], ...] — inverter do GeoJSON [lon, lat]

    React Router v7: pacote react-router-dom

    Backend espera form-urlencoded no login

    FormData no apiFetch: NÃO setar Content-Type manualmente

    <AuthProvider> no main.tsx — se faltar, useAuth explode em runtime

    Convenção: componentes = named export, páginas = default export

    <Link> dentro de <Link>: HTML inválido — thumb do ActivityCard é <img> + <span> dentro do <Link> pai, sem <Link> aninhado

    NavLink no header pra rota ativa

    Recharts 3.x: react-is peerDependency

    <img> com object-cover + h-32 corta fotos — usar aspect-square + object-cover (grid uniforme) ou object-contain (foto inteira). Aplicado no thumb do ActivityCard (h-24 w-24 + object-cover)

    Debounce de input é padrão recorrente — useDebounce já existe em web/src/hooks/useDebounce.ts; reusar em vez de duplicar

    useSearchParams + replace: true — sincronizar input debounced com URL sem encher histórico. Guard if (next === current) return evita loop de setSearchParams → useEffect.

    @tanstack/react-query: verificar import (@tanstack/react-query vs react-query v3). staleTime e enabled são iguais, import muda.

Ambiente / tooling

    .env nunca commitado; .env.local (web) também não

    Docker Desktop PRECISA estar aberto pra docker compose

    docker compose down -v NUNCA

    PowerShell curl é alias de Invoke-WebRequest — usar curl.exe ou Invoke-RestMethod

    Ordem de rotas: estáticas antes das dinâmicas

    npm sempre dentro de web/

    VS Code desatualizado: erro ts(2307) com arquivo existente → "TypeScript: Restart TS Server"

Usuários de teste

    Prod (Neon): prod@rumo.com / senha12345 (username produser); prod2@rumo.com / senha12345

    Local (Docker, não usado atualmente): teste@rumo.com / senha12345 (username testuser); teste2@rumo.com / senha12345

URLs de produção

    Backend: https://rumo-api-5s0b.onrender.com

    Docs: https://rumo-api-5s0b.onrender.com/docs

    Frontend: https://rumo-wheat.vercel.app

Comando de retomada para o próximo chat

    "Retomando o Rumo. Handoff anexo. Cinco blocos concluídos e testados em prod: 17 BACKEND (notificações), 17 FRONTEND, 17b BACKEND (cover_photo_url + photo_count, migração 517496af416f), 17b FRONTEND (thumbnail no ActivityCard), e busca de usuários (backend + frontend). Vamos começar o Bloco — Rate limiting (slowapi)."

Primeira ação no próximo chat

    Confirmar slowapi instalado no venv: cd D:\Rumo\backend; .\.venv\Scripts\Activate.ps1; pip show slowapi. Se não estiver, pip install slowapi e adicionar ao requirements.txt antes de qualquer outra coisa — senão o deploy no Render falha com ImportError.

    Pedir backend/app/routers/auth.py completo — pra adicionar @limiter.limit("5/minute") em POST /auth/login e 3/hour em POST /auth/register, e adicionar request: Request no signature dos dois.

    Pedir backend/app/routers/activities.py completo (ou ao menos as partes de POST /activities e POST /activities/{id}/photos) — pra decorar 10/hour e 20/hour respectivamente, e adicionar request: Request.

    Pedir backend/app/routers/users.py — já temos o conteúdo completo neste handoff (bloco 4 acima), mas confirmar que o POST /activities/{id}/photos real está em photos.py (não em activities.py), e que o search já está com @limiter.limit("20/minute").

    Entregar: core/rate_limit.py (novo), main.py completo (com app.state.limiter, exception handler, e middleware se necessário), requirements.txt completo com slowapi na seção de segurança, e os arquivos de router completos com decorators + request: Request.

    pip freeze no venv pra confirmar versão do slowapi (esperado 0.1.9+) e compatibilidade com starlette do FastAPI 0.115.6.