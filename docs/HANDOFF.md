hoje
HANDOFF — Rumo (backend + frontend + infra)

Data: 2026-10-20 (encerramento de sessão)
Duração da sessão: longa — 3 blocos entregues + validações extensas
Contexto: chegando ao limite; este handoff é para retomar amanhã com o próximo chat.
Resumo da sessão

Três blocos concluídos e testados em produção nesta sessão:

    Busca de atividades (feature nova) — backend GET /activities/search + frontend abas no /search

    GET /activities/{id}/photos com validação de permissão — furo de privacidade fechado

    Upload FIT (Bloco 12b) — parser fitparse + detecção por extensão + fallback haversine

Estado do app em prod: estável. Rate limiting cirúrgico, paginação, author aninhado no detalhe, busca de usuários, busca de atividades, /photos com regra dono+seguidos, e agora upload FIT funcionando tecnicamente (validação completa pendente de um .fit real do Haylou).

Produção:

    Backend: https://rumo-api-5s0b.onrender.com

    Docs: https://rumo-api-5s0b.onrender.com/docs

    Frontend: https://rumo-wheat.vercel.app

Commits no main (origin/main = HEAD)

Ordem cronológica desta sessão (mais antigo → mais recente):

    feat: busca de atividades (GET /activities/search) com visibilidade dono+seguidos

    feat: busca de atividades no /search (abas usuarios/atividades)

    fix: GET /activities/{id}/photos valida permissao (dono ou seguidor)

    feat: upload FIT (Bloco 12b) — parser fitparse, deteccao por extensao, fallback haversine

    fix: import haversine_m no fit_service (nome publico apos refactor) — conserto do ImportError que quebrou o Render

    fix: typo ffrom -> from no import do fit_service

    fix: usar haversine_m na chamada do fallback no fit_service

    fix: FIT — skip (0,0) indoor, prioriza session.total_timer_time, expande sport map

    Atenção: os 4 primeiros commits do handoff anterior (c55501f, d6e0d1a, 1195183, c16ba61, 2198497) precedem esta sessão. Os commits do author aninhado e da paginação estão em main — não foram tocados.

1. Bloco — Busca de atividades ✅ CONCLUÍDO E TESTADO EM PROD
Backend

backend/app/services/follow_service.py

    Novo helper following_ids_subquery(user_id) (retorna Select, não executa). Fonte única da regra "dono + seguidos". Import novo: Select.

    is_following continua igual.

backend/app/services/feed_service.py

    Troca a subquery inline pela chamada do helper. Comportamento idêntico, SQL desduplicado.

backend/app/services/activity_service.py

    Novo search_activities(db, user_id, q, limit, offset):

        or_(Activity.title.ilike(pattern), Activity.description.ilike(pattern)) com pattern = f"%{clean_q}%"

        or_(Activity.user_id == user_id, Activity.user_id.in_(following_ids_subquery(user_id)))

        .options(selectinload(Activity.user)) (obrigatório pro FeedItemResponse)

        .order_by(Activity.started_at.desc())

        trim defensivo: q só espaços retorna [] sem ir ao banco

backend/app/routers/activities.py

    GET /activities/search (response_model=list[FeedItemResponse], @limiter.limit("20/minute"), request: Request no signature, q com min_length=2, max_length=100)

    Declarada antes de /{activity_id} — ordem crítica, validada em prod (teste 404 com UUID inexistente).

Frontend

web/src/hooks/useActivitySearch.ts (novo)

    Espelha useUserSearch: queryKey: ["activities", "search", trimmed], enabled: trimmed.length >= 2, staleTime: 30_000, retorna FeedItem[].

web/src/components/UserResults.tsx (novo — extraído do SearchPage)
web/src/components/ActivityResults.tsx (novo)

    Recebe query já debounced; renderiza <ActivityCard activity={item} author={item.author} /> (o card aceita activity + author como props separadas).

web/src/pages/SearchPage.tsx (reescrito)

    Abas Usuários/Atividades via ?tab=users|activities com default users (retrocompatível com ?q= antigo)

    q compartilhado entre abas; replace:true no sync de URL

    role="tablist" + aria-selected para acessibilidade

Validação em prod

    q=Caminhada → 3 itens (2× Prod2, 1× produser) com author aninhado ✅

    q=caminhada (minúsculo) → mesmos 3 (ILIKE case-insensitive) ✅

    q=a (1 char) → 422 (min_length) ✅

    GET /activities/00000000-... → 404 (prova ordem das rotas) ✅

    UI: 5/5 cenários sem falha (deep-link, persistência entre abas, navegação por card, guard do mínimo, case-insensitive) ✅

2. Bloco — GET /activities/{id}/photos com validação ✅ CONCLUÍDO
Arquivos modificados

backend/app/services/photo_service.py

    list_photos(db, activity_id, user_id) — ganhou user_id, chama activity_service.get_activity(db, user_id, activity_id, allow_following=True) antes da query de fotos.

    Import novo: from app.services import activity_service.

    _get_owned_activity mantido com 403 (escrita) — semântica diferente de get_activity (leitura social, 404).

    Docstrings explicam a distinção 403 vs 404 para o próximo dev não "consertar" por engano.

backend/app/routers/photos.py

    Rota GET recebe current_user: User (era _: User), passa current_user.id pro service.

    try/except ServiceError obrigatório — sem ele, NotFoundError sobe como 500 (não é HTTPException, é exceção custom do ServiceError).

Validação em prod (4 cenários)

    Dono vê próprias fotos → 200 com foto ✅

    Seguidor vê fotos do seguido → 200 com [] ✅

    Não-seguidor → 404 ✅ (era 200 antes da correção — furo fechado)

    Atividade inexistente → 404 (não 500) ✅

    Método de teste: unfollow temporário (DELETE /users/{id}/follow) logado como Prod2, testar 404, refollow (POST). Ambiente restaurado.

Nova dívida consciente registrada

    Inconsistência 403 vs 404: upload_photo/delete_photo usam 403 (escrita); get_activity/get_activity_track/list_photos usam 404 (leitura social). Decisão semântica deliberada. Não é bug. Revisitar só se o app virar público.

3. Bloco — Upload FIT (12b) ✅ CONCLUÍDO (validação técnica)
Backend

backend/app/services/fit_service.py (novo)

    parse_fit(file_bytes) -> dict — mesmo shape do parse_gpx (title, gpx_type, started_at, finished_at, duration_s, distance_m, elevation_gain_m, avg_pace_s_per_km, avg_speed_mps, track_points)

    Usa fitparse.FitFile(BytesIO(...)) + fit.get_messages("record") (API atual, não get_records_by_type legado)

    Coordenadas FIT em semicírculos: graus = semicírculos * (180.0 / 2**31) (constante _SEMICIRCLES_TO_DEG)

    Duração: session.total_timer_time tem prioridade (mais preciso com pausas); fallback finished_at - started_at

    Distância: distance do último record tem prioridade; fallback haversine nos pontos válidos

    _is_null_position(lat, lon): pula pontos onde ambos são 0 (indoor com GPS desligado). Aplicado no fallback haversine e em track_points

    FIT_SPORT_MAP expandido: running, trail_running, treadmill_running, indoor_running, walking, casual_walking, speed_walking, indoor_walking, hiking, cycling, road_biking, mountain_biking, indoor_cycling, gravel_cycling, e_biking, swimming, lap_swimming, open_water_swimming

    FIT_OTHER_SPORTS (documental, não usado no código): esportes FIT sem equivalente no ActivityType do Rumo (stand_up_paddleboarding, rowing, skiing, yoga, tennis, etc.) — documenta que "other" é intencional

    map_fit_sport(fit_sport) -> str — mapeia para ActivityType, default "other"

    Rejeita FIT sem record (< 2): BadRequestError("FIT não contém registros de atividade suficientes...") — cobre workouts/courses

    try/except Exception em volta de FitFile(...) → BadRequestError(f"FIT inválido: {exc}") (400, não 500)

backend/app/services/gpx_service.py

    _haversine_m renomeado para haversine_m (público) — o fit_service importa. 3 ocorrências: definição + 1 chamada interna no parse_gpx. Comportamento idêntico.

backend/app/services/activity_service.py

    Novo helper _normalize_upload_fields(title, activity_type, description, parsed_title, parsed_type, type_mapper) — extraído de create_activity_from_gpx

    create_activity_from_gpx chama o helper (comportamento idêntico)

    Novo create_activity_from_fit — espelha o GPX, usa map_fit_sport

    calories=None nos dois (dívida consciente — cálculo fica para bloco separado)

backend/app/routers/activities.py

    POST /upload aceita .gpx ou .fit:

        filename_lower = file.filename.lower(); is_gpx/is_fit booleanos

        Se nem gpx nem fit → 400 "Formato não suportado. Envie um arquivo .gpx ou .fit"

        Dispatch para create_activity_from_gpx ou create_activity_from_fit

    Rate limit 10/hour intacto

backend/requirements.txt

    fitparse>=1.2.0 adicionado na seção "GPX / FIT" (logo abaixo de gpxpy==1.6.2)

Frontend (PENDENTE)

    accept=".gpx,.fit" no <input> do upload (1 linha) — não foi feito, fica para próximo bloco

    Mensagem de erro "Envie .gpx ou .fit" na UI — não foi feito

    Contrato não mudou (endpoint é o mesmo), então o frontend atual continua funcionando com .gpx. O .fit está funcional via API mas não exposto na UI.

Validação em prod

    Upload de Activity.fit (sintético Garmin FIT SDK) → 201 com duration_s: 3601 (após ajuste), distance_m: 3600.0, elevation_gain_m: 1778.0, avg_pace_s_per_km: 1000, avg_speed_mps: 1.0, activity_type: "other" (stand_up_paddleboarding) ✅

    .txt (win.ini) → 400 {"detail":"Formato não suportado. Envie um arquivo .gpx ou .fit"} ✅

    FIT corrompido (100 bytes aleatórios) → 400 {"detail":"FIT inválido: Invalid .FIT File Header"} ✅

    GPX zero regressão: não validado nesta sessão (arquivo placeholder). Pendente: subir D:\Caminhada_vespertina.gpx e confirmar 201.

    Atividades sintéticas do teste (01a156be... e 01a156ce...) apagadas do banco ✅

Risco registrado

    O Activity.fit usado não é do Haylou — é sintético do SDK Garmin (manufacturer: 'development', serial: 1234, product: 0). Sem .fit real do Haylou, não sabemos se o parser cobre o firmware do dispositivo. Não bloqueia: o Haylou exporta GPX (já testado) e o GPX é o caso real do usuário.

Estado atual dos arquivos-chave
Backend

    main.py — rate limit registrado; routers com prefixos; lifespan testa Postgres + PostGIS

    core/rate_limit.py — limiter + rate_limit_handler (429 com {"detail": "Muitas requisições..."})

    core/dependencies.py — get_current_user (JWT, 403 se inativo)

    routers/auth.py — login 5/min, register 3/hour, me sem limite

    routers/users.py — /search 20/min; follow/unfollow/followers/following/get_user sem limite

    routers/activities.py — novo /search 20/min antes de /{id}; POST "" e POST /upload 10/hour; GET /{id} retorna ActivityDetailResponse; stats/likes sem limite; /upload aceita .gpx ou .fit

    routers/photos.py — GET agora valida permissão (dono+seguidor); POST 20/hour; DELETE sem limite

    routers/feed.py — GET "" aceita limit/offset (default 20, max 100)

    schemas/activity.py — ActivityResponse, ActivityDetailResponse (com author), FeedItemResponse (com author), ActivityListResponse, TrackResponse

    schemas/photo.py — ActivityPhotoResponse (intacto)

    services/activity_service.py — novo search_activities, novo create_activity_from_fit, novo _normalize_upload_fields; get_activity com selectinload(Activity.user)

    services/follow_service.py — novo following_ids_subquery

    services/feed_service.py — usa following_ids_subquery (desduplicado)

    services/photo_service.py — list_photos valida permissão; upload síncrono; _recalc_cover_and_count no delete

    services/fit_service.py (NOVO) — parse_fit, map_fit_sport, FIT_SPORT_MAP, FIT_OTHER_SPORTS, _is_null_position

    services/gpx_service.py — haversine_m público (era _haversine_m)

Frontend

    hooks/useActivities.ts — useInfiniteQuery; useActivity com useQuery<ActivityDetail>

    hooks/useSocial.ts — useFeed com useInfiniteQuery<FeedItem[]>

    hooks/useUserSearch.ts — React Query, queryKey: ["users","search",trimmed], enabled: trimmed.length >= 2, staleTime: 30_000

    hooks/useActivitySearch.ts (NOVO) — espelha o padrão do useUserSearch

    hooks/useDebounce.ts — useDebounce<T>(value, delay = 300)

    components/ActivityCard.tsx — recebe activity: Activity + author?: UserPublic (props separadas)

    components/UserResults.tsx (NOVO) — extraído do SearchPage

    components/ActivityResults.tsx (NOVO) — renderiza ActivityCard com activity + author

    pages/SearchPage.tsx — reescrito com abas (?tab=users|activities, default users)

    pages/ActivitiesPage.tsx, FeedPage.tsx, ProfilePage.tsx — botão "Carregar mais"

    pages/ActivityDetailPage.tsx — lê activity.author direto

    types/api.ts — ActivityDetail, FeedItem (extends Activity { author })

    api/activities.ts — getActivity retorna ActivityDetail

Dívidas conhecidas (atualizadas nesta sessão)
Backend

    FIT_SPORT_MAP pode estar incompleto para firmwares específicos — sem .fit real do Haylou, não sabemos. FIT_OTHER_SPORTS documenta os intencionais.

    Upload de foto síncrono (bloqueia event loop ~1–3s) — decisão consciente de não tornar assíncrono agora

    Delete de foto no Cloudinary silencia exceção (foto órfã possível)

    GET /activities/{id} aceita dono OU seguidor — decisão is_public em aberto (pulada na sessão anterior)

    calories NULL no upload GPX e FIT — dívida barata, próximo bloco recomendado

    Sem testes automatizados

    UserResponse expõe email/birth_date

    GET /activities/{id}/comments exige auth

    Upload GPX síncrono

    Cold start do Render free tier

    Stats só do current_user

    Sem índice pg_trgm para busca (full scan OK até ~5k users/atividades; criar GIN gin_trgm_ops quando crescer)

    Inconsistência 403 (escrita) vs 404 (leitura social) — documentada, não é bug

    ~~GET /activities/{id}/photos não valida permissão~~ ← RESOLVIDO

    ~~Busca de atividades~~ ← RESOLVIDO

    ~~Upload FIT~~ ← RESOLVIDO (validação técnica; UI pendente)

Frontend

    .fit não exposto na UI de upload (só .gpx no accept) — pendente

    Mensagem de erro "Envie .gpx ou .fit" — pendente

    Contagem de likes no card do feed é local (não persiste)

    Mapa sem layer switcher

    Tipos em src/types/api.ts não gerados do OpenAPI

    react-hooks/set-state-in-effect desabilitada no ESLint

    Sem tratamento global de 401 pós-login

    client.ts: as string no VITE_API_URL (cast desnecessário)

    ActivityCard fallback "Atividade" genérico

    Upload sem rascunho / AbortController

    SearchPage sincroniza q na URL com replace: true — revisar se histórico precisar ser preservado

    Paginação: botão "Carregar mais" não validado visualmente em prod por falta de >20 itens

Infra

    Docker Desktop precisa estar aberto para docker compose local

    .env local aponta para Neon (prod) ou Docker — conferir antes de qualquer alembic

    Cloudinary free tier: 25 créditos/mês

    vercel.json precisa estar em web/

    .vscode/settings.json tem python.defaultInterpreterPath errado no Windows (era .venv/bin/python; corrigido para .venv/Scripts/python.exe nesta sessão) — se o repo versionar .vscode, pushar.

    fitparse no requirements.txt — se Render falhar com ModuleNotFoundError, verificar se o requirements.txt foi pushado junto (aconteceu com slowapi antes)

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

    ✅ Busca de atividades

    ✅ GET /activities/{id}/photos com validação

    ✅ Upload FIT (backend validado; UI pendente)

    ⏳ Cálculo de calorias no upload (GPX + FIT) ← PRÓXIMO RECOMENDADO

    ⏳ Upload de foto assíncrono — pulado consciente

    ⏳ is_public no GET /activities/{id} — pulado consciente

    ⏳ UI do upload FIT (accept + mensagem)

    ⏳ Bloco 14a: Mobile Flutter mínimo

Fase 3 — Diferenciais Strava (segments, leaderboards, achievements) — longo prazo
Preferências do usuário (CRÍTICO — seguir sempre)

    Sempre seguir a recomendação do chat — não oferecer A/B/C. O usuário confia na recomendação e quer ser direcionado.

    Avisar quando o contexto estiver perto do limite e gerar handoff completo. Não interromper o fluxo sem aviso.

    Handoff completo só quando o contexto apertar.

    Preferência por arquivos completos — quando um arquivo existente muda, entregar o arquivo inteiro (não diff, não "adicione estas linhas"). Reforçado: sempre arquivo completo, sem exceção.

    Explicações didáticas com o "porquê" — concisas mas com justificativa técnica.

    Comentários/docstrings em português; nomes em inglês.

    Commits em português: feat:, fix:, chore:, docs:.

    Sempre incluir os comandos de commit (PowerShell) quando for commitar.

    Testar direto em produção. Build local só para garantir TS/ESLint limpos antes do push.

    Blocos incrementais: implementar → testar (em prod) → commitar.

Armadilhas conhecidas (atualizadas nesta sessão)
Backend / Python

    bcrypt==4.0.1 obrigatório (4.1+ quebra passlib)

    greenlet==3.1.1 explícito (Python 3.13)

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso

    selectinload obrigatório quando schema acessa relação em async

    Alembic autogenerate só detecta model se importado em app/models/__init__.py

    alembic revision cria o arquivo; alembic upgrade head aplica

    venv é D:\Rumo\backend\.venv (com ponto): .\.venv\Scripts\Activate.ps1

    python global NÃO tem fitparse — sempre ativar o venv antes de rodar scripts Python. Erro clássico: ModuleNotFoundError porque o prompt era PS D:\Rumo> (sem (.venv)).

    cloudinary.uploader.upload é síncrono; aceita bytes; destroy(public_id) retorna {result: "not found"} sem exception se errado

    Pydantic v2: campo str obrigatório rejeita null

    include_router COM prefix + router que já declara prefix = /prefix/prefix

    IntegrityError no flush → rollback → só então criar notificação

    Rotas estáticas ANTES das dinâmicas — /users/search, /activities/search, /stats/* antes de /{id}

    slowapi: exige request: Request no signature do endpoint decorado. Sem ele, falha silenciosamente.

    @limiter.limit(...) entre @router.get/post(...) e async def.

    get_remote_address lê X-Forwarded-For; memory storage por processo (1 worker no free tier = ok)

    ServiceError NÃO herda de HTTPException — try/except ServiceError no router é obrigatório em rotas que chamam services que levantam NotFoundError/BadRequestError. Sem ele, erro vira 500.

    Renomear símbolo entre módulos: Select-String pelo nome ANTIGO em todos os arquivos tocados antes de commitar. Ex: _haversine_m → haversine_m ficou residual no fit_service e quebrou o Render (ImportError na subida).

    fitparse API: get_messages("record") (atual), não get_records_by_type (legado). Coordenadas em semicírculos: * (180.0 / 2**31). FitFile(BytesIO(...)) — envolver em try/except para virar 400, não 500.

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    WKT LINESTRING: ordem (lon lat)

    Dev: PG 16.4 + PostGIS 3.4; Prod: PG 17.11 + PostGIS 3.5

    Neon: PostGIS NÃO vem habilitado (CREATE EXTENSION IF NOT EXISTS postgis;); Postgres 18 NÃO tem PostGIS no Neon (usar 17)

    Neon: connection string Direct com asyncpg, ssl=require, sem channel_binding

    ILIKE com %termo% NÃO usa índice B-tree — full scan em /users/search e /activities/search

Render

    Free tier dorme após 15 min

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head &&

    requirements.txt PRECISA ir no commit — senão deploy falha com ModuleNotFoundError. Aconteceu com slowapi e com fitparse.

    Deploy Failed com ImportError: o traceback mostra a linha exata. Sintoma clássico: renomeou símbolo num arquivo, esqueceu de atualizar o import em outro. Sempre rodar python -c "from app.main import app; print('ok')" (ou import do módulo tocado) ANTES do push.

    CLOUDINARY_URL: colar só o valor, sem prefixo, sem aspas

    Deploy pode ficar velho se arquivos não foram pushados juntos

Cloudinary

    Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

    SDK Python lê do ambiente

    secure_url é a URL HTTPS; public_id é para deletar

    URL original sem transform — thumb do ActivityCard usa secure_url direto (cada transformação consome crédito)

Vercel

    vercel.json em web/ (Root Directory)

    SPA fallback obrigatório

    Env vars VITE_* só client-side

Frontend / Vite 8 / React 19 / Tailwind 3

    Vite 8 usa Rolldown — build.manualChunks objeto quebrou TS; usar build.rolldownOptions.output.codeSplitting.groups com { name, test: /regex/ }

    erasableSyntaxOnly: true — proíbe enum, namespace, parameter properties

    noUnusedLocals + noUnusedParameters ativos

    Tailwind fixado em tailwindcss@3

    react-leaflet v5 + React 19: importar "leaflet/dist/leaflet.css" no main.tsx

    MapContainer precisa de height explícita

    <Polyline> espera [[lat, lng], ...] — inverter do GeoJSON [lon, lat]

    React Router v7: react-router-dom

    Backend espera form-urlencoded no login

    FormData no apiFetch: NÃO setar Content-Type manualmente

    <AuthProvider> no main.tsx — sem ele, useAuth explode

    Componentes = named export, páginas = default export

    <Link> dentro de <Link>: HTML inválido

    Recharts 3.x: react-is peerDependency

    <img> com object-cover + h-32 corta fotos — usar aspect-square

    useInfiniteQuery: data é { pages: T[][], pageParams }; data?.pages.flat() ?? []; initialPageParam obrigatório (v5); refetchOnWindowFocus: false crítico

    React.lazy exige export default

    ActivityCard recebe activity: Activity + author?: UserPublic como props separadas (não FeedItem). Busca usa <ActivityCard activity={item} author={item.author} /> — FeedItem extends Activity, encaixa direto.

    Colagem errada de arquivo: o sintoma é Select-String não retornar, ou ruff check apontar SyntaxError: Simple statements must be separated... — sinal de arquivo corrompido (linhas grudadas, ffrom, etc.). Sempre validar conteúdo no disco antes de buildar/commitar.

    apiFetch NÃO adiciona query string — o caller monta com ?q=${encodeURIComponent(...)}&limit=20.

Ambiente / tooling

    .env nunca commitado; .env.local (web) também não

    Docker Desktop PRECISA estar aberto para docker compose

    docker compose down -v NUNCA

    PowerShell curl é alias de Invoke-WebRequest — usar curl.exe ou Invoke-RestMethod

    Invoke-RestMethod com $variable no path: sempre interpolar ("$url/$id"), nunca colar <placeholder> literal — o FastAPI rejeita com 422.

    Ordem de rotas: estáticas antes das dinâmicas

    npm sempre dentro de web/

    VS Code desatualizado: ts(2307) com arquivo existente → "TypeScript: Restart TS Server"

    VS Code Pylance + Python no Windows: python.defaultInterpreterPath precisa apontar para .venv/Scripts/python.exe (não .venv/bin/python, que é layout Unix). Se o Pylance reclamar reportMissingImports mesmo depois de pip install, Ctrl+Shift+P → "Python: Restart Language Server".

    git status antes de commitar é obrigatório — confirmar número exato de arquivos

    Token no localStorage: chave é rumo.token (com ponto)

    Checklist de commit de arquivo Python:

        ruff check <arquivo> → All checks passed!

        python -c "from <modulo> import <simbolo>; print('ok')" → ok

        Select-String nos símbolos críticos

        Select-String no nome antigo de símbolos renomeados (zero linhas)

        Só então git add + commit + push

FIT (novo)

    fitparse.FitFile(BytesIO(bytes)), get_messages("record"), get_messages("session"), get_messages("file_id")

    Coordenadas em semicírculos: graus = semicírculos * (180.0 / 2**31)

    session.total_timer_time (pausa) vs total_elapsed_time (relógio) — usar total_timer_time para duração real

    record.distance é acumulada em metros (se existir); fallback haversine

    record.speed em m/s

    FIT de workout/course não tem record → rejeitar

    file_id.manufacturer = 'development' + serial = 1234 = arquivo sintético do SDK, não de relógio real

    Indoor com GPS desligado grava position_lat = 0 e position_long = 0 — _is_null_position filtra

    Arquivo com lat = 0 e lon > 0 (caso do Activity.fit sintético) é coordenada legítima — não filtrar

Usuários de teste

    Prod (Neon): prod@rumo.com / senha12345 (username produser); prod2@rumo.com / senha12345 (username Prod2)

    Local (Docker, não usado atualmente): teste@rumo.com / senha12345 (username testuser); teste2@rumo.com / senha12345

    Relação de follow: produser segue Prod2 (confirmado em feed e busca)

    IDs conhecidos (prod):

        Usuário produser: 01a12c83-be2a-71fa-b966-1c93ca64f341

        Usuário Prod2: 01a141e7-5ea4-7600-8959-19145475ad0a

        Atividade do produser (com foto): 01a137b4-7e23-7d25-8ad2-dbcfed9ae1ec

        Atividades do Prod2: 01a141e7-b043-7e89-8009-5295cf177af9, 01a14200-598e-773c-8c6a-5a5e5b3ff9d8

        Atividades sintéticas de teste FIT (01a156be..., 01a156ce...): apagadas

Próximo bloco recomendado: cálculo de calorias no upload (GPX + FIT)
Por que esse

    É a única dívida barata restante no web com impacto direto de produto: calorias aparecem em /stats/summary, /stats/weekly, /stats/monthly e no detalhe da atividade — hoje todas mostram vazio.

    ~25–30 min, sem migração (campo calories já existe nullable), sem dependência nova.

    Usa o GPX que o usuário já tem (e o FIT que acabamos de implementar) — não depende de arquivo externo novo.

    Não conflita com nenhuma feature em andamento.

Escopo provável

    Backend:

        Novo helper _estimate_calories(activity_type, duration_s, weight_kg) no activity_service (ou calories.py novo)

        Fórmula: calories = MET × weight_kg × duration_hours

        MET por tipo: run=9.8, walk=3.5, cycle=7.5, hike=6.0, swim=8.0, other=5.0 (Compendium of Physical Activities, hardcoded num dict documentado, fácil de ajustar)

        weight_kg do usuário (current_user.weight_kg); fallback 70 kg se NULL (peso médio adulto, documentado)

        Aplicar em create_activity_from_gpx e create_activity_from_fit quando calories vier None do parse

        ActivityCreate (JSON manual): usuário pode mandar calories explícito e o valor dele prevalece — só calcula quando vier None

        Sem migração. User.weight_kg já existe (confirmar nome no models/user.py — o UserResponse mostra weight_kg: number | null)

    Frontend: nenhuma mudança necessária (o campo calories já aparece em stats/detalhe se preenchido).

    Validação em prod:

        Upload do Caminhada_vespertina.gpx → calories > 0 (esperado: ~360 kcal se for 1h de caminhada com 70kg; 3.5 × 70 × 1.0 ≈ 245 se MET=3.5)

        Upload do Activity.fit → calories > 0

        Comparar com o que o Strava/Haylou mostra pra mesma atividade (aproximação aceitável)

        stats/summary → total_calories deixa de ser 0/None

Primeira ação no próximo chat

Pedir ao usuário os arquivos:

    backend/app/models/user.py (confirmar weight_kg no model)

    backend/app/services/activity_service.py (estado atual — já tenho a versão desta sessão, mas confirmar se não mudou)

Com esses dois, montar o plano final + arquivos completos (activity_service.py com helper de calorias). Não precisa de gpx_service.py nem fit_service.py — o cálculo é pós-parse, no activity_service.
Alternativa se o usuário quiser algo diferente

    UI do upload FIT (accept .fit + mensagem "Envie .gpx ou .fit") — 1 arquivo frontend, ~10 min. Complementa o bloco FIT desta sessão.

    Bloco 14a: Mobile Flutter mínimo — frente nova, melhor com web mais redondo.

    Testes automatizados (dívida grande) — escopo aberto, melhor num bloco dedicado.

Recomendação: calorias primeiro (fecha a última dívida barata de produto), depois UI do FIT (fecha o bloco desta sessão), depois avaliar Flutter.
Observações finais para o próximo chat

    O bloco FIT está tecnicamente validado, mas a validação em prod do GPX zero-regressão ficou pendente — você mencionou D:\Caminhada_vespertina.gpx mas não chegou a rodar o upload. Primeira coisa a fazer: subir esse GPX e confirmar 201, depois apagar a atividade. É a prova que faltou do bloco 12b.

    O .fit real do Haylou não foi testado — só o sintético do SDK Garmin. Registrado como risco aceitável (o GPX cobre o caso do usuário).

    A UI não expõe .fit ainda — o endpoint aceita via API, mas o <input> do frontend só aceita .gpx. Se você quiser, o próximo chat adiciona isso (1 linha) antes ou junto do bloco de calorias.

    Commits dos fixes de FIT (ffrom, _haversine_m residual, skip (0,0)) — todos em main. O Render está com a última versão (duration_s: 3601 confirmado em prod).

    .vscode/settings.json foi corrigido localmente (python.defaultInterpreterPath → .venv/Scripts/python.exe). Se .vscode está no .gitignore, não vai pro repo — se não está, decidir se versiona.

    Contexto desta sessão chegou ao limite — este handoff é completo. Próximo chat começa limpo com o contexto do bloco de calorias.

Fim do handoff. Bom descanso, amanhã seguimos com o cálculo de calorias.