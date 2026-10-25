HANDOFF — Rumo (backend + frontend + infra)

Data de encerramento: 2026-10-25
Duração da sessão: longa — 1 bloco entregue (calorias) + 1 diagnóstico de deploy + decisão de exibição pendente
Contexto: chegou ao limite; este handoff é para retomar em novo chat.
Resumo da sessão

Bloco entregue e validado em produção:

    Cálculo de calorias no upload (GPX + FIT + JSON) — _estimate_calories (MET × peso × horas), _get_user_weight_kg, aplicado em create_activity, create_activity_from_gpx, create_activity_from_fit. Valores validados em prod: GPX → 248, FIT → 350.

Diagnóstico importante (registrar):

    O deploy do Render ficou velho após o push inicial do commit de calorias. O sintoma foi calories: null em prod mesmo com o código no GitHub e o log de build mostrando Your service is live. A causa nunca foi 100% confirmada, mas o problema sumiu depois de um novo push (commit de debug). Lição: se o Render mostrar Your service is live mas o comportamento for do código antigo, forçar um novo deploy (push qualquer ou Manual Deploy) resolve. O log sentinela de debug ficou no histórico (e6899f5) e foi removido em eb92676.

Pendência aberta:

    Exibição de calorias na UI — o backend devolve calories (validado: 248 e 350), o tipo Activity tem calories: number | null (web/src/types/api.ts:34), mas nenhum componente renderiza. Confirmado com Get-ChildItem -Recurse | Select-String "calories": só types/api.ts aparece. Falta mostrar em ActivityDetailPage.tsx (detalhe) e StatsPage.tsx/ProfilePage.tsx (total_calories). Decisão: não mostrar no ActivityCard.tsx (polui o feed; Strava não mostra).

Produção

    Backend: https://rumo-api-5s0b.onrender.com

    Docs: https://rumo-api-5s0b.onrender.com/docs

    Frontend: https://rumo-wheat.vercel.app

    Repo local: D:\Rumo

Commits no main (origin/main = HEAD)

Ordem cronológica desta sessão:

    340dfd9 — feat: estimativa de calorias no upload (MET x peso x duracao) para GPX, FIT e JSON

    c51ee2c — docs: atualiza HANDOFF com o estado da sessao

    e6899f5 — debug: log sentinela para verificar runtime do calculo de calorias

    eb92676 — chore: remove log sentinela do calculo de calorias apos validacao em prod

Atenção: e6899f5 é commit de debug e está no histórico. Não é problema — foi removido em eb92676. Commits anteriores (31e274a e antes) precedem esta sessão.
Estado do código (backend)

    services/activity_service.py — completo e limpo (sem log sentinela). Contém:

        _MET_BY_TYPE (run=9.8, walk=3.5, cycle=7.5, hike=6.0, swim=8.0, other=5.0), _MET_DEFAULT=5.0, _DEFAULT_WEIGHT_KG=70.0

        _estimate_calories(activity_type, duration_s, weight_kg) -> int | None — retorna None se duração ausente/0; int(round()) + clamp max(0, ...)

        _get_user_weight_kg(db, user_id) -> float — 1 query, fallback 70 kg

        create_activity, create_activity_from_gpx, create_activity_from_fit — todos calculam se calories is None

    models/user.py — weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True). Asyncpg devolve Decimal, _get_user_weight_kg faz float(weight).

    models/activity.py — calories: Mapped[int | None] com Integer + CheckConstraint("calories IS NULL OR calories >= 0", name="ck_calories_non_negative").

Estado do código (frontend)

    web/src/pages/UploadPage.tsx — PENDENTE DE APLICAR. Recebi a versão completa com accept=".gpx,.fit,..." + isSupportedFile + mensagem "Envie um arquivo .gpx ou .fit", mas não foi colado nem commitado. O arquivo atual no disco ainda aceita só .gpx. Próximo chat deve colar o arquivo completo (está no histórico da conversa anterior) e commitar.

    web/src/types/api.ts — Activity.calories: number | null (linha 34), Stats.total_calories: number (linhas 118, 129). Tipos OK.

    Nenhum componente renderiza calories/total_calories.

Pendências imediatas (fechar ANTES do próximo bloco)

P1 — Aplicar a UI do FIT (upload)

O UploadPage.tsx completo já foi preparado (com isSupportedFile, accept=".gpx,.fit,application/gpx+xml,application/vnd.garmin.fit", mensagens novas). Basta colar, npm run build, commitar e testar em prod. ~5 min.

P2 — Exibir calorias na UI

    ActivityDetailPage.tsx: adicionar calories na grade de métricas (junto com distância, pace, elevação).

    StatsPage.tsx/ProfilePage.tsx: renderizar total_calories no resumo.

    Não mexer no ActivityCard.tsx (decisão: não poluir o feed).

    Antes de entregar, pedir os 2 arquivos completos ao usuário.

P3 — Decisão de mobile Flutter

Não iniciado. Frente nova. Melhor depois de fechar P1/P2.
Dívidas conhecidas (atualizadas)

Backend:

    FIT_SPORT_MAP pode estar incompleto para firmwares específicos (sem .fit real do Haylou)

    Upload de foto síncrono

    Delete de foto no Cloudinary silencia exceção

    GET /activities/{id} aceita dono OU seguidor (is_public em aberto)

    ~~calories NULL no upload~~ ← RESOLVIDO nesta sessão

    Sem testes automatizados

    UserResponse expõe email/birth_date

    GET /activities/{id}/comments exige auth

    Upload GPX/FIT síncrono

    Cold start do Render free tier

    Stats só do current_user

    Sem índice pg_trgm para busca

    Inconsistência 403 (escrita) vs 404 (leitura social) — documentada

Frontend:

    ~~.fit não exposto na UI~~ ← PENDENTE DE APLICAR (arquivo pronto)

    ~~Mensagem de erro "Envie .gpx ou .fit"~~ ← PENDENTE DE APLICAR

    Calorias não exibidas em lugar nenhum ← P2

    Contagem de likes no card é local

    Mapa sem layer switcher

    Tipos não gerados do OpenAPI

    react-hooks/set-state-in-effect desabilitada no ESLint

    Sem tratamento global de 401 pós-login

    client.ts: as string no VITE_API_URL

    ActivityCard fallback "Atividade" genérico

    Upload sem rascunho / AbortController

    SearchPage replace: true

Infra:

    Docker Desktop precisa estar aberto para compose local

    .env local aponta para Neon (prod) ou Docker

    Cloudinary free tier: 25 créditos/mês

    vercel.json em web/

    .vscode/settings.json corrigido localmente (.venv/Scripts/python.exe), mas .vscode/ é ignorado pelo .gitignore:18 — não versionar

    Render pode ficar com deploy velho mesmo mostrando Your service is live. Se o comportamento for do código antigo, forçar novo push/redeploy.

Roadmap atualizado

Fase 2 — Refinar (em andamento):

    ✅ Rate limiting, paginação, author aninhado, busca de usuários, busca de atividades, /photos com validação, upload FIT, cálculo de calorias

    ⏳ Aplicar UI do FIT (arquivo pronto)

    ⏳ Exibir calorias (detalhe + stats)

    ⏳ Bloco 14a: Mobile Flutter mínimo

    ⏳ Testes automatizados

Fase 3 — Diferenciais Strava — longo prazo
Preferências do usuário (CRÍTICO)

    Sempre seguir a recomendação do chat — não oferecer A/B/C

    Avisar quando o contexto estiver perto do limite e gerar handoff completo

    Handoff completo só quando o contexto apertar

    Preferência por arquivos completos (não diff, não "adicione estas linhas")

    Explicações didáticas com o "porquê"

    Comentários/docstrings em português; nomes em inglês

    Commits em português: feat:, fix:, chore:, docs:

    Sempre incluir comandos de commit (PowerShell)

    Testar direto em produção. Build local só para TS/ESLint limpos

    Blocos incrementais: implementar → testar (prod) → commitar

Armadilhas conhecidas (atualizadas nesta sessão)

Backend / Python:

    bcrypt==4.0.1 obrigatório

    greenlet==3.1.1 explícito

    uuid.uuid7 não existe — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso

    selectinload obrigatório em async

    Asyncpg + Numeric devolve Decimal — float() antes de multiplicar por MET

    alembic revision cria; alembic upgrade head aplica

    venv é D:\Rumo\backend\.venv (com ponto)

    cloudinary.uploader.upload é síncrono

    Pydantic v2: str obrigatório rejeita null

    include_router COM prefix + router que já declara prefix = /prefix/prefix

    IntegrityError → rollback → depois notificação

    Rotas estáticas ANTES das dinâmicas

    slowapi exige request: Request na signature

    ServiceError não herda de HTTPException — try/except no router é obrigatório

    Renomear símbolo: Select-String pelo nome antigo antes de commitar

    fitparse: get_messages("record") (atual), FitFile(BytesIO(...)) em try/except

    calories é Integer + CheckConstraint >= 0 — int(round()) + max(0, ...)

Banco / PostGIS:

    Alembic + PostGIS: filtro include_object no env.py

    WKT LINESTRING: ordem (lon lat)

    Neon: CREATE EXTENSION IF NOT EXISTS postgis;

    ILIKE %termo% NÃO usa B-tree

Render:

    Free tier dorme após 15 min

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head &&

    requirements.txt PRECISA ir no commit

    Deploy Failed com ImportError: traceback mostra a linha

    Deploy pode ficar velho mesmo com Your service is live no log. Sintoma: comportamento de código antigo, mas build log mostra checkout novo. Solução: forçar novo push/redeploy. Confirmado nesta sessão (calorias voltaram a funcionar após novo push).

Cloudinary:

    Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

    secure_url é a URL HTTPS; public_id é para deletar

Vercel:

    vercel.json em web/

    SPA fallback obrigatório

    Env vars VITE_* só client-side

Frontend / Vite 8 / React 19 / Tailwind 3:

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

    Select-String -Recurse NÃO existe no PowerShell 5.1. Usar Get-ChildItem -Recurse -Include *.ts,*.tsx | Select-String -Pattern "..."

Ambiente / tooling:

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

    Checklist de commit Python: ruff → python -c "from ... import ..." → Select-String símbolos → Select-String nome antigo → git add + commit + push

    Invoke-RestMethod com 204 vazio pode dar erro de parsing. Usar curl.exe -i para ver status real.

FIT:

    fitparse.FitFile(BytesIO(bytes)), get_messages("record"), get_messages("session"), get_messages("file_id")

    Coordenadas em semicírculos: * (180.0 / 2**31)

    session.total_timer_time (pausa) vs total_elapsed_time (relógio) — usar total_timer_time

    record.distance acumulada em metros

    record.speed em m/s

    FIT de workout/course não tem record → rejeitar

    file_id.manufacturer = 'development' + serial = 1234 = sintético

    Indoor com GPS desligado: position_lat = 0 e position_long = 0 → filtrar

    parse_fit atual NÃO extrai total_calories — sempre cai no _estimate_calories. Dívida futura.

Usuários e IDs de teste

Prod (Neon):

    prod@rumo.com / senha12345 — username produser, id 01a12c83-be2a-71fa-b966-1c93ca64f341

    prod2@rumo.com / senha12345 — username Prod2, id 01a141e7-5ea4-7600-8959-19145475ad0a

    produser segue Prod2

Arquivos locais:

    D:\Activity.fit — sintético Garmin FIT SDK (94.096 bytes)

    D:\Caminhada_vespertina.gpx — GPX real

Atividades de teste: todas apagadas nesta sessão (banco limpo). Última criada (01a1743f-...) — apagar se ainda existir.
Próximo bloco recomendado

Fechar o tema de calorias: aplicar UI do FIT + exibir calorias.

Por que:

    O UploadPage.tsx completo já está pronto (no histórico anterior) — só colar e commitar. ~5 min.

    A exibição de calorias (detalhe + stats) é o que falta para o usuário ver o valor que o backend calcula. ~20 min, 2 arquivos.

    Fecha o tema por inteiro: backend calcula, UI aceita .fit, UI mostra kcal.

    Não abre frente nova (Flutter fica para depois).

Primeira ação no próximo chat

    Pedir ao usuário para colar o UploadPage.tsx completo (versão com .fit) e commitar.

    Pedir web/src/pages/ActivityDetailPage.tsx e web/src/pages/StatsPage.tsx (ou ProfilePage.tsx — onde os stats aparecem).

    Entregar os dois completos com calories/total_calories renderizados.

    Validar em prod (upload .fit via UI, ver kcal no detalhe e no resumo).

    Limpar atividades de teste.

Observações finais para o próximo chat

    A sessão anterior fechou o backend de calorias com sucesso. GPX → 248, FIT → 350, validado em prod. Não mexer nesse código sem motivo.

    O bug do Render (deploy velho com log "live") foi real. Registrar como armadilha: se o comportamento for do código antigo, forçar novo deploy.

    O UploadPage.tsx com .fit foi preparado mas NÃO aplicado. É a primeira coisa a fazer.

    A exibição de calorias é uma pendência real — confirmada com busca correta (Get-ChildItem -Recurse). Só types/api.ts tem o campo; nenhum componente renderiza.

    Contexto desta sessão chegou ao limite — handoff completo.

Salve isso em docs/HANDOFF.md (substituindo o atual), faça o commit docs: handoff da sessao de calorias + diagnostico de deploy, e no próximo chat abra com:

    "Retomando o Rumo. Handoff anexo. Backend de calorias fechado (GPX 248, FIT 350 validados em prod). Pendências: (P1) aplicar UploadPage.tsx com .fit (arquivo pronto no handoff anterior), (P2) exibir calorias em ActivityDetailPage.tsx + StatsPage.tsx. Vamos lá."