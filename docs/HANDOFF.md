Estado do projeto

Produção funcionando (Render + Vercel + Neon + Cloudinary). Todos os blocos até 17 FRONTEND (notificações) concluídos e testados em prod. Bloco 17b BACKEND (cover_photo_url + photo_count) concluído agora — aguardando commit/push (usuário vai fazer).
O que foi feito neste chat
1. Bloco 17 FRONTEND — Notificações in-app ✅ CONCLUÍDO E TESTADO EM PROD

Arquivos entregues e commitados:

    web/src/types/api.ts — tipos NotificationType, NotificationActivityPreview, Notification, UnreadCountResponse, MarkAllReadResponse

    web/src/api/notifications.ts (novo) — listNotifications, getUnreadCount, markNotificationRead, markAllNotificationsRead

    web/src/hooks/useNotifications.ts (novo) — notificationsKeys, useNotifications, useUnreadCount (polling 30s), useMarkRead, useMarkAllRead

    web/src/components/NotificationBell.tsx (novo) — sino SVG + badge (99+ cap), badge some se count=0

    web/src/pages/NotificationsPage.tsx (novo) — lista, navegação por tipo (follow → /users/{actor.id}, like/comment → /activities/{activity.id}), marca lida no clique, "marcar todas como lidas", empty state, link "← Voltar" pra /feed

    web/src/App.tsx — rota /notifications protegida + React.lazy em ActivityDetailPage e ProfilePage + <Suspense>

    web/src/components/AppHeader.tsx — sino no desktop (ao lado do username) + no topo do drawer mobile + item "Notificações" no nav do drawer

    web/src/vite.config.ts — build.rolldownOptions.output.codeSplitting.groups (Vite 8/Rolldown; manualChunks objeto quebrou o TS → solução: groups com name + test regex). Grupos: leaflet (leaflet|react-leaflet), recharts (recharts|react-is)

Testado em prod com 2 usuários (prod@rumo.com / prod2@rumo.com):

    follow/like/comment geram notificação ✅

    badge polling 30s ✅

    navegação correta por tipo ✅

    idempotência (unfollow→follow, unlike→like não duplicam) ✅

    auto-ação skip (curtir/comentar a própria atividade não notifica) ✅

    "marcar todas como lidas" zera badge ✅

    drawer mobile com sino + item nav ✅

    client.ts verificado: já tem guard de 204 (if (res.status === 204) return undefined as T;) — sem mudança necessária

Code splitting: build passou, chunk principal caiu, warning de 500kB sumiu.
2. Bloco 17b BACKEND — cover_photo_url + photo_count ✅ CONCLUÍDO

Decisão arquitetural: Opção A — denormalização no model Activity (não subquery, não endpoint separado). Justificativa: Strava-faithful, query de feed barata, from_attributes=True mantido nos schemas, fonte da verdade continua em activity_photos mas só photo_service escreve os denormalizados.

Arquivos entregues (completos, usuário aplicou):

    backend/app/models/activity.py — adicionados cover_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True) e photo_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0") + CheckConstraint("photo_count >= 0", name="ck_photo_count_non_negative") em __table_args__

    backend/app/schemas/activity.py — adicionados cover_photo_url: str | None e photo_count: int em ActivityResponse (herda em FeedItemResponse)

    backend/app/services/photo_service.py — upload: se photo_count == 0 seta cover_photo_url = photo.url, sempre incrementa photo_count. Delete: await db.flush() no DELETE, depois _recalc_cover_and_count(db, activity) (nova função interna que faz SELECT das fotos ordenadas por created_at ASC, seta photo_count = len(photos) e cover_photo_url = photos[0].url if photos else None). Fonte da verdade = tabela, evita dessincronização

    backend/alembic/versions/517496af416f_add_cover_photo_url_and_photo_count_to.py — ADD COLUMN (cover_photo_url TEXT nullable; photo_count INTEGER NOT NULL DEFAULT '0') + backfill UPDATE ... FROM (subquery com ARRAY_AGG(url ORDER BY created_at ASC))[1] + CREATE CHECK CONSTRAINT

    backend/app/services/activity_service.py — INALTERADO

    backend/app/services/feed_service.py — INALTERADO

Migração aplicada: alembic current → 517496af416f (head) no banco do .env local (que aponta pra Neon/prod, ou Docker se estiver rodando). Backfill rodou. docker compose exec falhou porque Docker Desktop não estava aberto — cosmético, não bloqueante.

Status: commit + push pendentes pelo usuário:
powershell

cd D:\Rumo
git add .
git commit -m "feat: cover_photo_url + photo_count denormalizados (bloco 17b backend)"
git push origin main

Render rodará alembic upgrade head idempotentemente no deploy (já está no head → não faz nada).
⏳ PRÓXIMO PASSO: Bloco 17b FRONTEND — Thumbnail no ActivityCard
Escopo

Arquivos que mudam:

    web/src/types/api.ts — adicionar cover_photo_url: string | null e photo_count: number em Activity (interface base; FeedItem extends Activity herda automaticamente)

    web/src/components/ActivityCard.tsx — se cover_photo_url existe, renderiza thumbnail; se não, layout atual. Precisa receber o arquivo completo atual do usuário pra devolver completo.

Decisão de design pendente (decidir no próximo chat)

Duas opções de layout do thumbnail no card:

    A) Faixa lateral (thumbnail à esquerda, conteúdo à direita) — funciona bem em lista vertical de cards, comum no Strava

    B) Thumbnail no topo do card (faixa horizontal, aspect-video ou similar) — mais visual, mas empurra conteúdo pra baixo em lista longa

Recomendação minha (a passar pro próximo chat): A — faixa lateral com h-24 w-24 (ou h-20 w-20) + object-cover + rounded, porque:

    Não altera altura do card drasticamente em feed com muitas atividades

    Consistente com a dívida registrada no handoff original ("Thumbnail de foto no ActivityCard do feed")

    Strava-like

    Se photo_count > 1, badge com contagem sobreposto no canto do thumbnail (padrão Strava)

Alternativa se o usuário preferir: thumbnail no topo com aspect-[4/3] ou aspect-square. Perguntar ao usuário no início do próximo chat.
Contexto crítico pro próximo chat

    Padrão de exports: ActivityCard é named export (export function ActivityCard)

    ActivityCard é usado em: FeedPage.tsx, ActivitiesPage.tsx, ProfilePage.tsx — mudança no card impacta os 3. Testar todos após implementar

    <Link> dentro de <Link> é HTML inválido: no ActivityCard atual, o card inteiro é <Link> e dentro tem LikeButton com e.preventDefault() + e.stopPropagation(). Se for adicionar thumbnail, NÃO colocar <Link> no thumbnail — usar <img> dentro do <Link> existente

    Thumbnail com object-cover + aspect-square: usar h-24 w-24 shrink-0 overflow-hidden rounded-lg (ou dimensão escolhida) + object-cover pra manter uniformidade. Já usamos esse padrão no PhotoGallery

    Fallback: se cover_photo_url é null, não renderizar o bloco de thumbnail (não usar placeholder "sem foto" — polui o feed)

    Badge de contagem: se photo_count > 1, mostrar contagem sobreposta (ex: <span className="absolute bottom-1 right-1 rounded bg-black/60 px-1.5 py-0.5 text-[10px] font-medium text-white">+{photo_count - 1}</span> ou similar). Mostra photo_count total, não -1 — decidir no chat

    sizes/loading: <img> com loading="lazy" + decoding="async" (performance)

    Fotos no Cloudinary: secure_url já vem em cover_photo_url. Não precisa transformar (free tier: cada transformação conta crédito; usar a URL original é o mais barato)

Pontos de atenção

    O card do feed (FeedPage) já é FeedItem que tem author: UserPublic — o thumbnail deve funcionar nos 3 contextos (feed, minhas atividades, perfil) sem distinção

    Após implementar, npm run build (checar TS/ESLint) → commit + push → testar em prod:

        Atividade com foto → thumbnail visível no card (feed, lista, perfil)

        Atividade sem foto → sem bloco de thumbnail (layout atual)

        Atividade com 2+ fotos → badge de contagem visível

        Clicar no thumbnail/card → navega pra /activities/{id} (comportamento atual preservado)

        Like no card continua funcionando (não quebrar o e.preventDefault())

Dívidas conhecidas (atualizadas)
Backend

    GET /activities/{id}/photos não valida permissão de visualização

    Upload de foto síncrono (bloqueia event loop ~1–3s)

    Delete de foto no Cloudinary silencia exceção (foto órfã possível)

    GET /activities/{id} aceita dono OU seguidor. Decisão em aberto: is_public?

    GET /activities/{id} não aninha author (2 requests no frontend) — ainda pendente

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

    ~~Thumbnail de foto no ActivityCard~~ → em resolução neste bloco

    useUserActivities fixa limit=20 — sem paginação

    Contagem de likes no card do feed é local (não persiste)

    Mapa sem layer switcher

    Tipos em src/types/api.ts não gerados do OpenAPI

    react-hooks/set-state-in-effect desabilitada no ESLint

    Sem tratamento global de 401 pós-login

    client.ts: as string no VITE_API_URL (cast desnecessário)

    ActivityCard fallback "Atividade" genérico

    Upload sem rascunho / AbortController

    Sem busca de usuários ← gargalo de produto real (usuário não acha ninguém no app; teste do bloco 17 escancarou isso)

    Bundle: resolvido via code splitting (leaflet + recharts separados)

Infra

    Docker Desktop precisa estar aberto pra docker compose local

    .env local aponta pra Neon (prod) ou Docker — conferir antes de qualquer alembic comando pra não aplicar migração no banco errado

    Cloudinary free tier: 25 créditos/mês

    vercel.json precisa estar em web/

Roadmap atualizado (fases)

    Fase 1 — Deploy + primeira feature ✅

    Fase 2 — Refinar o que existe (em andamento):

        ✅ Bloco 16: Perfil + stats visuais

        ✅ Bloco 15: Fotos (Cloudinary)

        ✅ Fixes pós-15

        ✅ Bloco 17 BACKEND: Notificações

        ✅ Bloco 17 FRONTEND: Notificações

        ✅ Bloco 17b BACKEND: cover_photo_url + photo_count

        ⏳ Bloco 17b FRONTEND: thumbnail no ActivityCard ← PRÓXIMO

        ⏳ Busca de usuários ← recomendação forte pós-17b (gargalo de produto)

        ⏳ Bloco 12b: Upload FIT (opcional, se tiver relógio)

        ⏳ Bloco 14a: Mobile Flutter mínimo

    Fase 3 — Diferenciais Strava (segments, leaderboards, achievements) — longo prazo

Ordem de recomendação para próximos blocos

    Bloco 17b FRONTEND (thumbnail no ActivityCard) — fecha a dívida #1, ~30min

    Busca de usuários (GET /users/search?q= backend + input no header ou /search page frontend) — feature nova, maior lacuna de produto, destrava descoberta social

    Rate limiting (slowapi) — protege free tier

    is_public no GET /activities/{id} — decisão de produto pendente

    Code splitting ✅ já feito

    cover_photo_url ✅ já feito

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

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    WKT LINESTRING: ordem (lon lat)

    Dev: PG 16.4 + PostGIS 3.4; Prod: PG 17.11 + PostGIS 3.5

    Neon: PostGIS NÃO vem habilitado (CREATE EXTENSION IF NOT EXISTS postgis;); Postgres 18 NÃO tem PostGIS no Neon (usar 17)

    Neon: connection string Direct com asyncpg, ssl=require, sem channel_binding

Render

    Free tier dorme após 15 min

    rootDir: backend no render.yaml

    startCommand com alembic upgrade head &&

    CLOUDINARY_URL: colar só o valor, sem prefixo, sem aspas

    Deploy Failed com ImportError: conferir git ls-files + nome exato do símbolo

Cloudinary

    Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME

    CLOUDINARY_URL no Render: só o valor

    SDK Python lê do ambiente

    secure_url é a URL HTTPS; public_id é pra deletar

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

    Link dentro de <Link>: HTML inválido — usar <div> wrapper

    NavLink no header pra rota ativa

    Recharts 3.x: react-is peerDependency

    <img> com object-cover + h-32 corta fotos — usar aspect-square + object-cover (grid uniforme) ou object-contain (foto inteira). Aplicar no thumbnail do ActivityCard.

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

    "Retomando o Rumo. Handoff anexo. Bloco 17b BACKEND concluído (cover_photo_url + photo_count denormalizados, migração 517496af416f aplicada). Vamos começar o Bloco 17b FRONTEND (thumbnail no ActivityCard)."

Primeira ação no próximo chat:

    Confirmar que o usuário fez commit + push do backend (bloco 17b)

    Pedir web/src/components/ActivityCard.tsx completo (pra devolver completo)

    Pedir web/src/types/api.ts atual (pra confirmar que já tem os tipos do bloco 17 e adicionar cover_photo_url/photo_count em Activity)

    Confirmar decisão de design (faixa lateral recomendada, ou topo) — recomendar faixa lateral direto, conforme preferência do usuário por "seguir a recomendação"

    Implementar → npm run build → commit + push → testar em prod nos 3 contextos (feed, minhas atividades, perfil)