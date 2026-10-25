# HANDOFF — Rumo (backend + frontend + infra)

Data de encerramento: 2026-10-25 (sessão 2 — fechamento de calorias)
Duração da sessão: curta — P1 + P2 fechados e validados em prod
Contexto: sessão encerrada com o tema de calorias 100% concluído.
Próximo bloco recomendado: testes automatizados no backend.

## Resumo da sessão

Tema de calorias fechado de ponta a ponta:

- Backend calcula (`_estimate_calories`, MET × peso × horas) — validado em prod
  na sessão anterior (GPX → 248, FIT → 350).
- UI aceita `.fit` no upload — commit `21957cf`, validado em prod.
- UI exibe calorias no detalhe e no resumo de stats — commit `253e6bb`,
  validado em prod (detalhe mostra kcal; stats mostra total_calories;
  ActivityCard intocado por decisão).

Banco de teste: limpar antes do próximo bloco (2 atividades geradas nesta
sessão para validação).

## Produção

- Backend: https://rumo-api-5s0b.onrender.com
- Docs: https://rumo-api-5s0b.onrender.com/docs
- Frontend: https://rumo-wheat.vercel.app
- Repo local: D:\Rumo

## Commits no main (origin/main = HEAD = 253e6bb)

- 253e6bb — feat: exibe calorias no detalhe da atividade e no resumo de stats
- 21957cf — feat: aceita .fit no upload (UI) e mensagem de erro .gpx/.fit
- eb92676 — chore: remove log sentinela do calculo de calorias apos validacao em prod
- e6899f5 — debug: log sentinela (histórico, removido em eb92676)
- c51ee2c — docs: atualiza HANDOFF
- 340dfd9 — feat: estimativa de calorias no upload (MET x peso x duracao)

## Estado do código (backend) — inalterado nesta sessão

services/activity_service.py — completo e limpo:

- _MET_BY_TYPE (run=9.8, walk=3.5, cycle=7.5, hike=6.0, swim=8.0, other=5.0),
  _MET_DEFAULT=5.0, _DEFAULT_WEIGHT_KG=70.0
- _estimate_calories(activity_type, duration_s, weight_kg) -> int | None —
  retorna None se duração ausente/0; int(round()) + clamp max(0, ...)
- _get_user_weight_kg(db, user_id) -> float — 1 query, fallback 70 kg
- create_activity, create_activity_from_gpx, create_activity_from_fit —
  todos calculam se calories is None

models/user.py — weight_kg: Numeric(5, 2), nullable. Asyncpg devolve Decimal,
_get_user_weight_kg faz float(weight).

models/activity.py — calories: Integer, nullable, CheckConstraint
"calories IS NULL OR calories >= 0".

## Estado do código (frontend)

- web/src/pages/UploadPage.tsx — aceita .gpx e .fit (isSupportedFile,
  accept=".gpx,.fit,application/gpx+xml,application/vnd.garmin.fit",
  mensagem "Envie um arquivo .gpx ou .fit"). Validado em prod.
- web/src/lib/format.ts — formatCalories(kcal) adicionada, padrão pt-BR
  (toLocaleString), retorna "—" para null/undefined. Reutilizável no mobile.
- web/src/pages/ActivityDetailPage.tsx — grade de métricas agora tem 5 cards
  (Distância, Duração, Pace, Elevação, Calorias). Grid:
  grid-cols-2 md:grid-cols-3 lg:grid-cols-5.
- web/src/components/StatsCards.tsx — 5 cards no resumo (Atividades, Distância,
  Tempo, Elevação, Calorias). Grid: grid-cols-2 sm:grid-cols-3 lg:grid-cols-5.
  Skeleton acompanha (5 placeholders).
- web/src/components/ActivityCard.tsx — NÃO exibe calorias (decisão mantida).
- web/src/types/api.ts — Activity.calories: number | null,
  StatsSummary.total_calories: number. Tipos OK.

## Pendências imediatas

Nenhuma bloqueante. Bloco de calorias fechado.

## Próximo bloco recomendado — Testes automatizados no backend

Motivo: maior dívida técnica isolada. Calorias é caso ideal para o primeiro
teste (função pura, determinística). Não abre frente nova (Flutter fica depois).

Escopo do bloco:

- Infraestrutura: pytest + pytest-asyncio + httpx. AsyncClient,
  fixtures para banco de teste (pode usar SQLite in-memory ou Postgres de teste),
  pytest.ini, tests/__init__.py, tests/conftest.py
- Cobertura mínima inicial:
  - _estimate_calories (run/walk/cycle/hike/swim/other + custom types + None/0)
  - _get_user_weight_kg (com weight_kg definido, null → fallback 70)
  - Upload de GPX (rota) — verifica que activity.calories é int e > 0
  - Upload de FIT (rota) — idem
- Não cobrir tudo na primeira sessão — infraestrutura + bloco de calorias.
  Blocos posteriores (social, stats, upload foto) ganham teste conforme avançam.

## Dívidas conhecidas (atualizadas)

### Backend

- FIT_SPORT_MAP pode estar incompleto para firmwares específicos
- Upload de foto síncrono
- Delete de foto no Cloudinary silencia exceção
- GET /activities/{id} aceita dono OU seguidor (is_public em aberto)
- Sem testes automatizados ← ALVO DO PRÓXIMO BLOCO
- UserResponse expõe email/birth_date
- GET /activities/{id}/comments exige auth
- Upload GPX/FIT síncrono
- Cold start do Render free tier
- Stats só do current_user
- Sem índice pg_trgm para busca
- Inconsistência 403 (escrita) vs 404 (leitura social)
- parse_fit NÃO extrai total_calories do FIT — sempre cai no _estimate_calories

### Frontend

- Contagem de likes no card é local
- Mapa sem layer switcher
- Tipos não gerados do OpenAPI
- react-hooks/set-state-in-effect desabilitada no ESLint
- Sem tratamento global de 401 pós-login
- client.ts: as string no VITE_API_URL
- ActivityCard fallback "Atividade" genérico
- Upload sem rascunho / AbortController
- SearchPage replace: true

### Infra

- Docker Desktop precisa estar aberto para compose local
- .env local aponta para Neon (prod) ou Docker
- Cloudinary free tier: 25 créditos/mês
- vercel.json em web/
- .vscode/settings.json corrigido localmente (.venv/Scripts/python.exe),
  mas .vscode/ é ignorado — não versionar
- Render pode ficar com deploy velho mesmo mostrando "Your service is live".
  Sintoma: comportamento de código antigo. Solução: novo push/redeploy manual.
  Confirmado em sessão anterior.

## Roadmap atualizado

### Fase 2 — Refinar (em andamento)

- ✅ Rate limiting, paginação, author aninhado, busca de usuários,
     busca de atividades, /photos com validação, upload FIT,
     cálculo de calorias, UI do FIT, exibição de calorias
- ⏳ Testes automatizados no backend ← PRÓXIMO
- ⏳ Bloco 14a: Mobile Flutter mínimo
- ⏳ Demais dívidas da lista

### Fase 3 — Diferenciais Strava — longo prazo

## Preferências do usuário (CRÍTICO)

- Sempre seguir a recomendação do chat — não oferecer A/B/C
- Avisar quando o contexto estiver perto do limite e gerar handoff completo
- Handoff completo só quando o contexto apertar
- Preferência por arquivos completos (não diff, não "adicione estas linhas")
- Explicações didáticas com o "porquê"
- Comentários/docstrings em português; nomes em inglês
- Commits em português: feat:, fix:, chore:, docs:
- Sempre incluir comandos de commit (PowerShell)
- Testar direto em produção. Build local só para TS/ESLint limpos
- Blocos incrementais: implementar → testar (prod) → commitar

## Armadilhas conhecidas (atualizadas)

### Backend / Python

- bcrypt==4.0.1 obrigatório
- greenlet==3.1.1 explícito
- uuid.uuid7 não existe — usar from uuid6 import uuid7
- DateTime sem timezone=True — bug silencioso
- selectinload obrigatório em async
- Asyncpg + Numeric devolve Decimal — float() antes de multiplicar por MET
- alembic revision cria; alembic upgrade head aplica
- venv é D:\Rumo\backend\.venv (com ponto)
- cloudinary.uploader.upload é síncrono
- Pydantic v2: str obrigatório rejeita null
- include_router COM prefix + router que já declara prefix = /prefix/prefix
- IntegrityError → rollback → depois notificação
- Rotas estáticas ANTES das dinâmicas
- slowapi exige request: Request na signature
- ServiceError não herda de HTTPException — try/except no router é obrigatório
- Renomear símbolo: Select-String pelo nome antigo antes de commitar
- fitparse: get_messages("record"), FitFile(BytesIO(...)) em try/except
- calories é Integer + CheckConstraint >= 0 — int(round()) + max(0, ...)

### Banco / PostGIS

- Alembic + PostGIS: filtro include_object no env.py
- WKT LINESTRING: ordem (lon lat)
- Neon: CREATE EXTENSION IF NOT EXISTS postgis;
- ILIKE %termo% NÃO usa B-tree

### Render

- Free tier dorme após 15 min
- rootDir: backend no render.yaml
- startCommand com alembic upgrade head &&
- requirements.txt PRECISA ir no commit
- Deploy Failed com ImportError: traceback mostra a linha
- Deploy pode ficar velho mesmo com "Your service is live". Forçar novo push.

### Cloudinary

- Formato: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
- secure_url é a URL HTTPS; public_id é para deletar

### Vercel

- vercel.json em web/
- SPA fallback obrigatório
- Env vars VITE_* só client-side

### Frontend / Vite 8 / React 19 / Tailwind 3

- Vite 8 usa Rolldown — build.manualChunks objeto quebrou TS
- erasableSyntaxOnly: true
- noUnusedLocals + noUnusedParameters ativos
- tailwindcss@3 fixo
- react-leaflet v5 + React 19: importar CSS no main.tsx
- MapContainer precisa height explícita
- <Polyline> espera [[lat, lng], ...]
- React Router v7: react-router-dom
- Backend espera form-urlencoded no login
- FormData no apiFetch: NÃO setar Content-Type
- <AuthProvider> no main.tsx
- Componentes = named export; páginas = default export
- <Link> dentro de <Link>: HTML inválido
- Recharts 3.x: react-is peerDependency
- <img> com object-cover + h-32 corta — usar aspect-square
- useInfiniteQuery: data.pages.flat() ?? []; initialPageParam obrigatório
- React.lazy exige export default
- ActivityCard recebe activity + author? (props separadas)
- Select-String -Recurse NÃO existe no PowerShell 5.1. Usar
  Get-ChildItem -Recurse -Include *.ts,*.tsx | Select-String -Pattern "..."
- toLocaleString("pt-BR") em número formata milhar com ponto — usar em
  formatCalories (não usar String(kcal) puro)

### Ambiente / tooling

- .env e .env.local nunca commitados
- Docker Desktop precisa estar aberto
- docker compose down -v NUNCA
- curl no PowerShell é alias de Invoke-WebRequest — usar curl.exe
- Invoke-RestMethod com $variable no path: sempre interpolar
- Ordem de rotas: estáticas antes das dinâmicas
- npm sempre dentro de web/
- VS Code: python.defaultInterpreterPath → .venv/Scripts/python.exe (Windows)
- git status antes de commitar
- Token no localStorage: rumo.token
- Checklist de commit Python: ruff → python -c "from ... import ..." →
  Select-String símbolos → Select-String nome antigo → git add + commit + push
- Invoke-RestMethod com 204 vazio pode dar erro de parsing.
  Usar curl.exe -i para ver status real.

### FIT

- fitparse.FitFile(BytesIO(bytes)), get_messages("record"), get_messages("session"),
  get_messages("file_id")
- Coordenadas em semicírculos: * (180.0 / 2**31)
- session.total_timer_time (pausa) vs total_elapsed_time (relógio) — usar
  total_timer_time
- record.distance acumulada em metros
- record.speed em m/s
- FIT de workout/course não tem record → rejeitar
- file_id.manufacturer = 'development' + serial = 1234 = sintético
- Indoor com GPS desligado: position_lat = 0 e position_long = 0 → filtrar
- parse_fit atual NÃO extrai total_calories — sempre cai no _estimate_calories

## Usuários e IDs de teste

Prod (Neon):

- prod@rumo.com / senha12345 — username produser,
  id 01a12c83-be2a-71fa-b966-1c93ca64f341
- prod2@rumo.com / senha12345 — username Prod2,
  id 01a141e7-5ea4-7600-8959-19145475ad0a
- produser segue Prod2

Arquivos locais:

- D:\Activity.fit — sintético Garmin FIT SDK (94.096 bytes)
- D:\Caminhada_vespertina.gpx — GPX real

Atividades de teste: geradas nesta sessão para validar calorias.
Limpar antes do próximo bloco (UI → Apagar atividade).

## Próximo bloco recomendado

Bloco de testes automatizados no backend.

Por quê:

- Maior dívida técnica isolada — backend sem nenhum teste.
- Calorias é caso ideal: _estimate_calories é função pura, determinística,
  fácil de cobrir com teste unitário.
- _get_user_weight_kg tem fallback → testar com weight_kg null e definido.
- Rotas de upload (GPX/FIT) cobrem integração end-to-end.
- Não abre frente nova (Flutter fica depois).
- Custo baixo: ~1 sessão para infraestrutura + cobertura do bloco de calorias.

Primeira ação no próximo chat:

1. Montar infraestrutura: requirements.txt (adicionar pytest,
   pytest-asyncio, httpx, aiosqlite ou asyncpg-test), pyproject.toml ou
   pytest.ini, tests/__init__.py, tests/conftest.py.
2. Escrever tests/test_calories.py cobrindo _estimate_calories e
   _get_user_weight_kg (unit) + rotas de upload GPX/FIT (integração).
3. Rodar pytest local, ajustar, commit.

## Observações finais para o próximo chat

- Tema de calorias encerrado — backend, UI de upload, UI de exibição (detalhe
  + stats). Nada a mexer nesse código sem motivo.
- Handoff anterior estava desatualizado em P1 e P2 — a sessão anterior
  deixou o UploadPage.tsx preparado mas sem aplicar; foi aplicado nesta sessão
  em commit 21957cf. P2 em 253e6bb.
- AtividadeCard.tsx continua sem calorias por decisão (não poluir feed).
- Banco tem 2 atividades de teste (GPX + FIT) — limpar antes do próximo bloco.
- Armadilha do Render (deploy velho com log "live") segue valendo — se o
  comportamento em prod for de código antigo, forçar novo deploy.