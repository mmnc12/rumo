HANDOFF — Rumo (backend + frontend + infra)
Resumo da sessão

Quatro blocos concluídos e testados em produção nesta sessão, além de duas decisões de produto registradas. O app está estável em prod: rate limiting cirúrgico com slowapi, paginação com "Carregar mais" em feed/activities/profile, author aninhado no GET /activities/{id} (economiza 1 request), e a decisão consciente de não tornar o upload de foto assíncrono agora.

Produção:

    Backend: https://rumo-api-5s0b.onrender.com (Render free tier)

    Docs: https://rumo-api-5s0b.onrender.com/docs

    Frontend: https://rumo-wheat.vercel.app (Vercel)

Últimos commits no main (origin/main = HEAD):

    c55501f — feat: paginacao com carregar mais em feed, activities e profile

    d6e0d1a — feat: paginacao com carregar mais em feed, activities e profile

    1195183 — feat: rate limiting cirúrgico com slowapi em auth, search e uploads

    c16ba61 — feat: busca de usuários (página /search + input no header + drawer)

    2198497 — feat: GET /users/search (busca por username/full_name)

    (commit do author aninhado foi feito após esta lista — está em main, HEAD atual)

1. Bloco — Rate limiting (slowapi) ✅ CONCLUÍDO E TESTADO EM PROD

Arquivos novos:

    backend/app/core/rate_limit.py — limiter = Limiter(key_func=get_remote_address) + rate_limit_handler retornando 429 com {"detail": "Muitas requisições. Tente novamente em instantes."}

Arquivos modificados:

    backend/app/main.py — app.state.limiter = limiter + app.add_exception_handler(RateLimitExceeded, rate_limit_handler). Sem SlowAPIMiddleware (limite cirúrgico, não global)

    backend/app/routers/auth.py — @limiter.limit("5/minute") em POST /login; @limiter.limit("3/hour") em POST /register; request: Request como primeiro parâmetro dos dois

    backend/app/routers/users.py — @limiter.limit("20/minute") em GET /search; request: Request no signature

    backend/app/routers/activities.py — @limiter.limit("10/hour") em POST "" (JSON) e em POST /upload (GPX); request: Request nos dois

    backend/app/routers/photos.py — @limiter.limit("20/hour") em POST /activities/{id}/photos; request: Request

    backend/requirements.txt — slowapi>=0.1.10 (na seção Segurança, após python-multipart==0.0.20)

Validado em prod:

    /users/search: requisições 1–20 → 200; 21–25 → 429 ✅

    /feed: 200 (não afetado — isolamento cirúrgico confirmado) ✅

    /health: {"status":"ok","database":"ok","ambiente":"production"} ✅

Decisão de design: limite por endpoint, não global. "Não punir usuário legítimo scrollando feed é mais importante que a ameaça." Memory storage do slowapi é por processo — Render free tier roda 1 worker, então funciona. Se escalar para múltiplos workers/instâncias, migrar para Redis (já no requirements.txt, ainda não usado).
2. Bloco — Paginação em feed/activities/profile ✅ CONCLUÍDO (backend validado; botão espera dados)

Arquivos modificados:

    web/src/hooks/useActivities.ts — useActivities e useUserActivities viraram useInfiniteQuery<Activity[]>. getNextPageParam: lastPage.length < limit → undefined; senão allPages.reduce((acc, p) => acc + p.length, 0). initialPageParam: 0

    web/src/hooks/useSocial.ts — useFeed virou useInfiniteQuery<FeedItem[]>. socialKeys.feed perdeu offset (agora (limit = 20) => ["feed", { limit }]). Resto (useActivityLikes, useToggleLike, useComments, useCreateComment, useDeleteComment, useFollowUser) intacto

    web/src/pages/ActivitiesPage.tsx — activities = data?.pages.flat() ?? []; botão "Carregar mais" com fetchNextPage/hasNextPage/isFetchingNextPage

    web/src/pages/FeedPage.tsx — mesmo padrão

    web/src/pages/ProfilePage.tsx — activitiesData?.pages.flat() ?? []; botão "Carregar mais" na seção Atividades; CTA de 403 intacto

Validação: backend confirmado via curl em prod — GET /activities?limit=2&offset=0 → 1 item; offset=2 → [] (correto). Frontend com lógica correta. Botão não validado visualmente em prod por falta de >20 itens (produser tem 1 atividade hoje). Comportamento esperado quando o volume crescer.

Decisão de design: botão "Carregar mais" (não scroll infinito). Mais simples, testável, sem IntersectionObserver. refetchOnWindowFocus: false no useFeed é crítico — sem isso, trocar de aba descarta as páginas seguintes.
3. Bloco — author aninhado no GET /activities/{id} ✅ CONCLUÍDO E TESTADO EM PROD

Arquivos modificados:

    backend/app/schemas/activity.py — novo ActivityDetailResponse(ActivityResponse) com author: UserPublic = Field(validation_alias="user"). FeedItemResponse intacto. ActivityResponse não ganhou author (listagem continua leve)

    backend/app/services/activity_service.py — get_activity ganhou .options(selectinload(Activity.user)) na stmt

    backend/app/routers/activities.py — GET /activities/{id} com response_model=ActivityDetailResponse

    web/src/types/api.ts — novo ActivityDetail extends Activity { author: UserPublic }

    web/src/api/activities.ts — getActivity retorna Promise<ActivityDetail>

    web/src/hooks/useActivities.ts — useActivity com useQuery<ActivityDetail> (era useQuery<Activity>)

    web/src/pages/ActivityDetailPage.tsx — removido useUser e a linha const { data: author } = useUser(...); lê activity.author.id/activity.author.username direto

Ganho: 1 request a menos por abertura de atividade (antes eram 2: /activities/{id} + /users/{id}).

Validado em prod: build limpo (chunk ActivityDetailPage 10.58 kB / gzip 3.70 kB), "por @username" aparece no topo, sem request extra de /users/{id}.
4. Decisões de produto registradas

is_public no GET /activities/{id} — PULADO (decisão A). Mantém a regra atual (dono OU seguidor recebe 200; resto 404). Justificativa: é feature nova com custo de migração + UI + decisão de produto, não é "refinar o que existe". Fila tem dívidas mais baratas e mais impactantes. Reavaliar quando houver necessidade real (ex: compartilhar link público de atividade).

Upload de foto assíncrono — PULADO (dívida consciente). cloudinary.uploader.upload() é síncrono e bloqueia o event loop ~1–3s. Tornar assíncrono exigiria: BackgroundTasks + retorno 202 sem a foto + polling no frontend + estado de "processando" na UI + tratamento de falha tardia. Custo (~1h, muda contrato, piora UX com estado de processamento) > benefício (economizar 1–3s em ação rara). Rate limit de 20/hora já mitiga abuso. Reavaliar se o volume de uploads crescer ou se o Cloudinary começar a demorar >5s.
Estado atual dos arquivos-chave

Backend:

    main.py — rate limit registrado; routers com prefixos; lifespan testa Postgres + PostGIS

    core/rate_limit.py — limiter + rate_limit_handler

    core/dependencies.py — get_current_user (JWT, 403 se inativo)

    routers/auth.py — login 5/min, register 3/hour, me sem limite

    routers/users.py — /search 20/min; follow/unfollow/followers/following/get_user sem limite

    routers/activities.py — POST "" e POST /upload 10/hour; GET /{id} retorna ActivityDetailResponse; stats/likes sem limite

    routers/photos.py — POST /activities/{id}/photos 20/hour; GET/DELETE sem limite

    routers/feed.py — GET "" aceita limit/offset (default 20, max 100)

    schemas/activity.py — ActivityResponse, ActivityDetailResponse (com author), FeedItemResponse (com author), ActivityListResponse, TrackResponse

    services/activity_service.py — get_activity com selectinload(Activity.user)

    services/photo_service.py — upload síncrono; _recalc_cover_and_count no delete (fonte da verdade = tabela)

Frontend:

    hooks/useActivities.ts — useActivities/useUserActivities com useInfiniteQuery; useActivity com useQuery<ActivityDetail>; useActivityTrack, useUploadGpx, useDeleteActivity intactos

    hooks/useSocial.ts — useFeed com useInfiniteQuery<FeedItem[]>; useToggleLike otimista; useFollowUser invalida ["feed"] + activitiesKeys.lists()

    hooks/useUserSearch.ts — React Query, queryKey: ["users", "search", trimmed], enabled: trimmed.length >= 2, staleTime: 30_000

    hooks/useDebounce.ts — useDebounce<T>(value, delay = 300)

    pages/ActivitiesPage.tsx, FeedPage.tsx, ProfilePage.tsx — botão "Carregar mais"

    pages/ActivityDetailPage.tsx — lê activity.author direto

    pages/SearchPage.tsx — busca de usuários com useSearchParams, deep-linkable /search?q=...

    types/api.ts — ActivityDetail adicionado

    api/activities.ts — getActivity retorna ActivityDetail

Dívidas conhecidas (atualizadas)

Backend:

    GET /activities/{id}/photos não valida permissão de visualização (qualquer autenticado lista fotos de qualquer atividade)

    Upload de foto síncrono (bloqueia event loop ~1–3s) — decisão consciente de não tornar assíncrono agora

    Delete de foto no Cloudinary silencia exceção (foto órfã possível)

    GET /activities/{id} aceita dono OU seguidor. Decisão is_public em aberto (pulada nesta sessão)

    ~~GET /activities/{id} não aninha author~~ ← RESOLVIDO

    calories NULL no upload GPX

    ~~Sem rate limiting~~ ← RESOLVIDO (memory storage; migrar para Redis se escalar workers)

    Sem testes automatizados

    UserResponse expõe email/birth_date

    GET /activities/{id}/comments exige auth

    Upload GPX síncrono

    Cold start do Render free tier

    Stats só do current_user

    Sem índice pg_trgm para busca (full scan OK até ~5k users; criar GIN gin_trgm_ops quando crescer)

Frontend:

    Contagem de likes no card do feed é local (não persiste)

    Mapa sem layer switcher

    Tipos em src/types/api.ts não gerados do OpenAPI

    react-hooks/set-state-in-effect desabilitada no ESLint

    Sem tratamento global de 401 pós-login

    client.ts: as string no VITE_API_URL (cast desnecessário)

    ActivityCard fallback "Atividade" genérico

    Upload sem rascunho / AbortController

    SearchPage sincroniza q na URL com replace: true — revisar se histórico precisar ser preservado

    Paginação: botão "Carregar mais" não validado visualmente em prod por falta de >20 itens (comportamento esperado quando o volume crescer)

Infra:

    Docker Desktop precisa estar aberto para docker compose local

    .env local aponta para Neon (prod) ou Docker — conferir antes de qualquer alembic comando

    Cloudinary free tier: 25 créditos/mês

    vercel.json precisa estar em web/

    Slowapi instalado no venv — se Render falhar com ImportError, é porque requirements.txt não foi pushado junto

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

    ✅ Rate limiting (slowapi)

    ✅ Paginação em feed/activities/profile

    ✅ author aninhado no GET /activities/{id}

    ⏳ Busca de atividades (feature nova) ← PRÓXIMO

    ⏳ Upload de foto assíncrono — pulado, dívida consciente

    ⏳ is_public no GET /activities/{id} — pulado, decisão A

    ⏳ Bloco 12b: Upload FIT (opcional, se tiver relógio)

    ⏳ Bloco 14a: Mobile Flutter mínimo

Fase 3 — Diferenciais Strava (segments, leaderboards, achievements) — longo prazo
Preferências do usuário (CRÍTICO — seguir sempre)

    Sempre seguir a recomendação do chat — não oferecer A/B/C. O usuário confia na recomendação e quer ser direcionado.

    Avisar quando o contexto estiver perto do limite e gerar handoff completo. Não interromper o fluxo sem aviso.

    Handoff completo só quando o contexto apertar.

    Preferência por arquivos completos — quando um arquivo existente muda, entregar o arquivo inteiro (não diff, não "adicione estas linhas"). Reforçado nesta sessão: sempre arquivo completo, sem exceção.

    Explicações didáticas com o "porquê" — concisas mas com justificativa técnica.

    Comentários/docstrings em português; nomes em inglês.

    Commits em português: feat:, fix:, chore:, docs:.

    Sempre incluir os comandos de commit (PowerShell) quando for commitar.

    Testar direto em produção. Build local só para garantir TS/ESLint limpos antes do push.

    Blocos incrementais: implementar → testar (em prod) → commitar.

Armadilhas conhecidas (atualizadas nesta sessão)

Backend / Python:

    bcrypt==4.0.1 obrigatório (4.1+ quebra passlib)

    greenlet==3.1.1 explícito (Python 3.13)

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso

    selectinload obrigatório quando schema acessa relação em async

    Alembic autogenerate só detecta model se importado em app/models/__init__.py

    alembic revision cria o arquivo; alembic upgrade head aplica

    venv é D:\Rumo\backend\.venv (com ponto): .\.venv\Scripts\Activate.ps1

    cloudinary.uploader.upload é síncrono; aceita bytes; destroy(public_id) retorna {result: "not found"} sem exception se errado

    Pydantic v2: campo str obrigatório rejeita null

    include_router COM prefix + router que já declara prefix = /prefix/prefix

    IntegrityError no flush → rollback → só então criar notificação

    Rotas estáticas ANTES das dinâmicas — /users/search antes de /users/{user_id}

    slowapi: exige request: Request no signature do endpoint decorado. Sem ele, falha silenciosamente (todas retornam 200). Decorator @limiter.limit(...) fica entre @router.get/post(...) e async def. Ordem invertida = não intercepta.

    slowapi + FastAPI module-level app: app.state.limiter = limiter + app.add_exception_handler(RateLimitExceeded, handler) após criar o app. Sem SlowAPIMiddleware se for limite cirúrgico.

    get_remote_address lê X-Forwarded-For quando presente — funciona atrás do proxy do Render. Memory storage é por processo (1 worker no free tier = ok).

    selectinload em get_activity: como get_activity é chamado por get_activity_track e delete_activity também, o selectinload faz uma query extra nesses casos. Custo desprezível (1 linha indexada por id). Não otimizar prematuramente.

    Import de ActivityDetail no useActivities.ts: se useActivity ficar useQuery<Activity>, o activity.author no ActivityDetailPage dá erro TS Property 'author' does not exist on type 'Activity'. Tem que ser useQuery<ActivityDetail>.

Banco / PostGIS:

    Alembic + PostGIS: filtro include_object no env.py

    WKT LINESTRING: ordem (lon lat)

    Dev: PG 16.4 + PostGIS 3.4; Prod: PG 17.11 + PostGIS 3.5

    Neon: PostGIS NÃO vem habilitado (CREATE EXTENSION IF NOT EXISTS postgis;); Postgres 18 NÃO tem PostGIS no Neon (usar 17)

    Neon: connection string Direct com asyncpg, ssl=require, sem channel_binding

    ILIKE com %termo% NÃO usa índice B-tree — full scan é o que roda hoje em /users/search

Render:

    Free tier dorme após 15 min

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head &&

    CLOUDINARY_URL: colar só o valor, sem prefixo, sem aspas

    Deploy Failed com ImportError: conferir git ls-files + nome exato do símbolo

    Deploy pode ficar velho se requirements.txt não for pushado junto — slowapi novo: adicionar ao requirements.txt E pushar junto

Cloudinary:

    Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

    SDK Python lê do ambiente

    secure_url é a URL HTTPS; public_id é para deletar

    URL original sem transform — thumb do ActivityCard usa secure_url direto (cada transformação consome crédito do free tier: 25/mês)

Vercel:

    vercel.json em web/ (Root Directory)

    SPA fallback obrigatório

    Env vars VITE_* só client-side

Frontend / Vite 8 / React 19 / Tailwind 3:

    Vite 8 usa Rolldown — build.manualChunks objeto quebrou TS; usar build.rolldownOptions.output.codeSplitting.groups com { name, test: /regex/ }

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

    <Link> dentro de <Link>: HTML inválido — thumb do ActivityCard é <img> + <span> dentro do <Link> pai

    Recharts 3.x: react-is peerDependency

    <img> com object-cover + h-32 corta fotos — usar aspect-square + object-cover ou object-contain

    useInfiniteQuery: data é { pages: T[][], pageParams: number[] }, não T[]. Acessar via data?.pages.flat() ?? []. getNextPageParam assume list[T] puro (sem envelope): lastPage.length < limit → undefined. isLoading só no primeiro fetch; isFetchingNextPage para os seguintes. refetchOnWindowFocus: false é crítico — sem isso, trocar de aba descarta as páginas seguintes

    React.lazy exige export default no módulo. Se o arquivo colado não tem export default, TS reclama Property 'default' is missing. Sempre confirmar com Select-String -Path <arquivo> -Pattern "export default" depois de colar

    Colagem errada de arquivo: nesta sessão, o useActivities.ts foi colado dentro do ActivityDetailPage.tsx. Sintoma: Select-String "export default" não retorna nada, e o Get-Content | Select-Object -First 5 mostra imports do hook em vez da página. Sempre validar o conteúdo no disco antes de buildar

    @tanstack/react-query: verificar import (@tanstack/react-query vs react-query v3). useInfiniteQuery exige initialPageParam (v5) — sem ele, TS quebra

Ambiente / tooling:

    .env nunca commitado; .env.local (web) também não

    Docker Desktop PRECISA estar aberto para docker compose

    docker compose down -v NUNCA

    PowerShell curl é alias de Invoke-WebRequest — usar curl.exe ou Invoke-RestMethod

    Ordem de rotas: estáticas antes das dinâmicas

    npm sempre dentro de web/

    VS Code desatualizado: erro ts(2307) com arquivo existente → "TypeScript: Restart TS Server"

    git status antes de commitar é obrigatório — confirmar o número exato de arquivos. Nesta sessão, um commit saiu com 1 arquivo quando deveriam ser 5 (arquivos não salvos no disco ou colados no lugar errado)

    Token no localStorage: a chave do Rumo é rumo.token (com ponto). Usar localStorage.getItem("rumo.token") em testes de console

Usuários de teste

    Prod (Neon): prod@rumo.com / senha12345 (username produser); prod2@rumo.com / senha12345

    Local (Docker, não usado atualmente): teste@rumo.com / senha12345 (username testuser); teste2@rumo.com / senha12345

Próximo bloco recomendado: Busca de atividades (feature nova)

Por que esse: é o próximo item da fila após os pulos conscientes (upload assíncrono, is_public). É feature nova, sem mudança de contrato existente, valor direto pro usuário (expande a busca de usuários para atividades). ~40–50min.

Escopo provável:

    Backend: GET /activities/search?q=&limit=&offset= com ILIKE em title/description (e talvez activity_type), filtrando por visibilidade (dono + seguidos — mesma regra do feed), rota estática antes de /{activity_id}. Schema de resposta provavelmente FeedItemResponse (com author aninhado) para o frontend renderizar ActivityCard com autor

    Frontend: expandir SearchPage.tsx com abas "Usuários" / "Atividades"; hook useActivitySearch com React Query + debounce; renderizar ActivityCard nos resultados

    Rate limit: adicionar @limiter.limit("20/minute") no novo endpoint (mesmo padrão do /users/search)

Primeira ação no próximo chat: pedir ao usuário os arquivos backend/app/routers/activities.py, backend/app/services/activity_service.py, backend/app/schemas/activity.py, web/src/pages/SearchPage.tsx, web/src/hooks/useUserSearch.ts (ou useActivitySearch se já existir) para montar o plano com base no estado real, não no handoff.

Alternativa se o usuário quiser algo menor: Bloco 12b (Upload FIT, opcional) ou Bloco 14a (Mobile Flutter mínimo). Mas busca de atividades é a recomendação.