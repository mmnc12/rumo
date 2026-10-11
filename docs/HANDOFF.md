# Rumo — Handoff Atualizado (após Bloco 11)

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
2. ⏳ **Bloco 13a: Frontend mínimo** (React/Vercel) — só:
   - Tela de login/registro
   - Tela de "minhas atividades" (lista)
   - Tela de upload GPX (arrasta arquivo → mostra que criou)
   - Tela de detalhe de atividade (mapa + métricas)
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
- **Backend:** Python 3.13.7 + FastAPI + SQLAlchemy 2.0 async + Alembic + GeoAlchemy2
- **Banco dev:** PostgreSQL 16.4 + PostGIS 3.4 (Docker, imagem `postgis/postgis:16-3.4`)
- **Banco prod:** Neon (PostGIS habilitado, projeto `rumo`, branch `production`, região AWS US East 2 Ohio, PG **17.11** + PostGIS **3.5**)
- **Cache:** Redis (Docker, ainda não usado)
- **Deploy backend:** Render (Blueprint via `render.yaml`, free tier)
- **Frontend:** Vercel (React, futuro) | **Mobile:** Flutter (futuro)
- **Repo:** https://github.com/mmnc12/rumo (privado)
- **IDE:** VS Code (terminal integrado)
- **OS:** Windows (PowerShell)

## Decisões arquiteturais
1. Async em tudo (SQLAlchemy async + asyncpg)
2. IDs UUID v7 via `from uuid6 import uuid7` (NÃO usar `uuid.uuid7` nativo — só existe em Python 3.14+)
3. PostGIS desde o início (rotas GPS como LINESTRING SRID 4326)
4. Config via `.env` + Pydantic Settings — `.env` NUNCA versionado
5. Alembic com filtro `include_object` (ignora tabelas de sistema PostGIS)
6. **`bcrypt==4.0.1` fixado** (4.1+ quebra passlib)
7. **`greenlet==3.1.1` explícito** no requirements (Python 3.13 não instala)
8. Ao gerar migração com `Geometry`: adicionar `import geoalchemy2` no topo E remover `op.create_index` do GIST
9. Senhas com bcrypt, JWT HS256, `get_current_user` como dependência reutilizável
10. Modelo `Activity` opção A: `route` LINESTRING + `raw_track_points` JSONB (sem tabela TrackPoint separada)
11. **Ordem de rotas no router:** rotas estáticas (`/stats/...`, `/upload`) declaradas ANTES das dinâmicas (`/{id}`)
12. **Pace/velocidade no summary são ponderados** (soma/soma), não média de médias
13. **`DateTime(timezone=True)` em TODAS as colunas de data/hora**
14. **`ServiceError` genérico** em `app/services/errors.py` com subclasses `NotFoundError` (404), `ConflictError` (409), `BadRequestError` (400), `ForbiddenError` (403). Routers traduzem `ServiceError` → `HTTPException` via helper.
15. **`lazy="raise"` nos `relationship()`** + `selectinload` explícito nos services que precisam carregar relações
16. **`FeedItemResponse` e `CommentResponse`** usam `validation_alias="user"` para mapear o ORM `*.user` → campo `author` no JSON.
17. **Routers de activities com prefixo no `main.py`** (`prefix="/activities"`)
18. **Router de comments SEM prefixo** — paths completos nos decorators
19. **`UserPublic`** (sem email/birth_date) para expor dados de outros usuários. `UserResponse` (com email) só para o próprio `/auth/me`.
20. **`track_points` formato único:** `[[lat, lon, ele, unix_ts], ...]` — usado tanto no POST JSON quanto no upload GPX. `points_to_linestring` monta o WKT na ordem `(lon lat)` (armadilha #5).
21. **Upload GPX:** `POST /activities/upload` (multipart). Parse com `gpxpy`, cálculo automático (Haversine, elevação com threshold 1m), popula `route` + `raw_track_points`. `title`/`activity_type`/`description` são opcionais e sobrescrevem o GPX se fornecidos. Validação defensiva contra placeholder `"string"` do Swagger.
22. **CORS configurado** via `CORSMiddleware` no `main.py`, lendo `settings.ALLOWED_ORIGINS` (formato JSON no `.env`).
23. **Deploy via Blueprint** (`render.yaml` na raiz) + `rootDir: backend` + `startCommand` com `alembic upgrade head && gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 2 --timeout 60`.
24. **`.env` local → Docker. Env vars do Render → Neon.** Nunca cruzar.

## Estrutura de pastas

D:\Rumo
├── .gitignore, README.md, docker-compose.yml, render.yaml ← render.yaml NOVO
├── docs\HANDOFF.md
├── backend
│ ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│ ├── _scratch\ (NÃO versionado — scripts descartáveis)
│ ├── samples\ (não versionado — GPX de teste)
│ ├── alembic\env.py + versions{users, activities, follows, likes, comments}
│ ├── app
│ │ ├── main.py, config.py, database.py
│ │ ├── core\security.py, core\dependencies.py
│ │ ├── models{user.py, activity.py, follow.py, like.py, comment.py, init.py}
│ │ ├── schemas{user.py, activity.py, stats.py, like.py, comment.py, init.py}
│ │ ├── routers{auth.py, activities.py, feed.py, users.py, comments.py, init.py}
│ │ └── services{activity_service.py, gpx_service.py, stats_service.py, follow_service.py, like_service.py, feed_service.py, comment_service.py, errors.py, init.py}
│ └── tests
├── mobile\ (vazio)
└── web\ (vazio)


## Models existentes

### User
- id (UUID v7), email (unique), username (unique), full_name
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

### Follow
- id (UUID v7), follower_id (FK users CASCADE), following_id (FK users CASCADE)
- created_at
- UNIQUE(follower_id, following_id), CHECK(follower_id <> following_id)

### Like
- id (UUID v7), user_id (FK users CASCADE), activity_id (FK activities CASCADE)
- created_at
- UNIQUE(user_id, activity_id)

### Comment
- id (UUID v7), user_id (FK users CASCADE), activity_id (FK activities CASCADE)
- content TEXT (limite 500 validado no schema)
- created_at, updated_at (`DateTime(timezone=True)`)
- Índices: user_id, activity_id. SEM UNIQUE (pode comentar várias vezes)
- `user = relationship("User", lazy="raise")` (com `TYPE_CHECKING` para o type hint)

## Endpoints existentes

### Auth & Users
- `GET /` — metadados
- `GET /health` — status API + banco
- `POST /auth/register` — cria usuário (201, 409 se duplicado)
- `POST /auth/login` — form-urlencoded (username=email), retorna JWT
- `GET /auth/me` — protegido, dados do usuário atual (UserResponse, com email)
- `POST /users/{user_id}/follow` — 204 (400 self, 404 target, 409 duplicado)
- `DELETE /users/{user_id}/follow` — 204 (404 se não segue)
- `GET /users/{user_id}/followers?limit&offset` — lista seguidores (UserPublic)
- `GET /users/{user_id}/following?limit&offset` — lista quem segue (UserPublic)

### Activities
- `POST /activities` — 201 (JSON pré-calculado, com `track_points` opcional)
- `POST /activities/upload` — 201 (multipart, arquivo `.gpx`, parse + cálculo automático)
- `GET /activities?limit=20&offset=0` — lista próprias atividades
- `GET /activities/{id}` — detalhes (só do dono)
- `DELETE /activities/{id}` — 204 (só do dono)
- `GET /activities/stats/summary?activity_type=` — totais gerais
- `GET /activities/stats/weekly?weeks=8&activity_type=` — últimas N semanas
- `GET /activities/stats/monthly?months=6&activity_type=` — últimos N meses
- `POST /activities/{id}/like` — 200 `{count, liked_by_me}` (idempotente)
- `DELETE /activities/{id}/like` — 204 (idempotente)
- `GET /activities/{id}/likes?limit&offset` — 200 `{count, liked_by_me, users[]}`

### Comments
- `POST /activities/{activity_id}/comments` — 201, `CommentResponse` com `author: UserPublic`
- `GET /activities/{activity_id}/comments?limit&offset` — 200, `list[CommentResponse]` (ordem ASC)
- `DELETE /comments/{comment_id}` — 204 (só autor; 403 se não for)

### Feed
- `GET /feed?limit=20&offset=0` — atividades próprias + de quem segue, com `author` (FeedItemResponse)

## Produção (Render + Neon)

- **API pública:** `https://rumo-api-XXXX.onrender.com` (você anota a sua URL)
- **Docs:** `https://rumo-api-XXXX.onrender.com/docs`
- **Banco:** Neon, projeto `rumo`, branch `production`, região AWS US East 2 (Ohio), PG 17.11 + PostGIS 3.5
- **Deploy:** Blueprint `render.yaml` na raiz do repo. `git push origin main` → Render detecta → rebuilda → redeploya (~2-5 min)
- **Free tier:** dorme após 15 min sem tráfego. Primeira request depois disso demora ~30-50s (cold start). Não é bug.
- **Env vars no Render:** `DATABASE_URL`, `ENVIRONMENT=production`, `DEBUG=false`, `SECRET_KEY` (gerada), `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `ALLOWED_ORIGINS=["http://localhost:5173"]`, `PYTHON_VERSION=3.13.7`
- **Conexão do Neon (formato pra asyncpg):**

postgresql+asyncpg://rumo_dev_owner:SENHA@ep-curly-queen-b4f7zqd3.c-6.us-east-2.aws.neon.tech/rumo_dev?ssl=require

(Direct connection, sem `-pooler`, sem `channel_binding`)

## Blocos concluídos
✅ 1 a 9 (ver histórico)
✅ 10a - Follows (tabela, endpoints de seguir/deixar de seguir/listar)
✅ 10b - Feed (atividades próprias + de quem segue, com autor enriquecido)
✅ 10c - Likes (curtir/descurtir/listar, idempotente)
✅ 10d - Comentários (criar/listar/deletar, 403 pra não-autor, ForbiddenError criado)
✅ 12 - Upload GPX + cálculo automático de métricas (parser, Haversine, elevação, PostGIS + JSONB, refatoração do activity_service)
✅ **11 - Deploy Render + Neon** (Blueprint, CORS, gunicorn, smoke test passou)

## Blocos pendentes
⏳ **13a - Frontend React mínimo** (login, lista, upload GPX, detalhe) — Fase 1, PRÓXIMO
⏳ 14a - Mobile Flutter mínimo — Fase 1
⏳ 12b - Upload FIT (opcional, formato binário com fitdecode/garmin-fit-sdk)
⏳ 13b/14b - Feed/likes/comentários no frontend/mobile — Fase 2
⏳ 15 - Fotos de atividade — Fase 2
⏳ 16 - Perfil público + stats visuais — Fase 2
⏳ 17+ - Segments, achievements, notificações, análise de treino — Fase 3

## Pendências técnicas (dívida para limpar)
1. **`calories` fica NULL no upload GPX** — cálculo precisa de peso + FC + tipo, é bloco separado.
2. **Sem upload de foto de atividade** — precisa de storage (S3/Cloudinary/R2).
3. **Sem rate limiting** — abuso de API é trivial.
4. **Redis não está sendo usado** (está no docker-compose mas não tem cache de feed/stats).
5. **Sem testes automatizados** — `tests/` ainda vazia.
6. **`UserResponse` expõe `email` e `birth_date`** — usado só em `/auth/me` (ok), mas vale revisar antes de prod.
7. **`GET /activities/{id}/comments` exige auth** — se quiser público depois, remover `Depends(get_current_user)`.
8. **Não há `/activities/{id}/route` ou `/track`** — o `ActivityResponse` não expõe `route` nem `raw_track_points` (decisão de performance). Se o frontend precisar desenhar o mapa, criar endpoint dedicado que retorna a geometria.
9. **Upload GPX é síncrono** — bloqueia o request por ~1s. No futuro, background com fila (arq/Celery/RQ).
10. **Cold start do Render free tier** — ~30-50s na primeira request após 15 min idle. Aceitável no MVP, mas pra usuário real no dia a dia, subir pro plano pago (~$7/mês) na Fase 2.
11. **`ALLOWED_ORIGINS` no Render aponta pra `http://localhost:5173`** — quando o frontend da Vercel existir, atualizar pra URL de produção.
12. **`SECRET_KEY` local e de prod são diferentes** — JWTs de dev não funcionam em prod e vice-versa. Correto por design, mas anotar.

## Comandos essenciais
```powershell
# Subir infra (Docker Desktop PRECISA estar aberto primeiro!)
cd D:\Rumo ; docker compose start
docker compose ps   # confere se postgres e redis estão healthy

# Rodar backend (TERMINAL SEPARADO, deixar aberto)
cd D:\Rumo\backend ; .venv\Scripts\Activate.ps1 ; uvicorn app.main:app --reload

# Alembic
alembic current
alembic revision --autogenerate -m "descricao"
alembic upgrade head
alembic downgrade -1

# Banco local (Docker)
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "\d activities"
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "\d comments"
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "SELECT id, title, activity_type, distance_m, ST_NPoints(route) AS n_points FROM activities ORDER BY created_at DESC LIMIT 5;"

# Testar parser GPX isolado (sem API)
cd D:\Rumo\backend ; .venv\Scripts\Activate.ps1
python -c "from app.services.gpx_service import parse_gpx; d = parse_gpx(open('samples/sample_run.gpx','rb').read()); print(d)"

# Testar Neon (produção) — criar _scratch/test_neon.py
python _scratch\test_neon.py

# Git
cd D:\Rumo ; git add . ; git commit -m "..." ; git push

Usuários de teste

Local (Docker):

    teste@rumo.com / senha12345 (id: 01a0f49c-8e6d-7506-a1c1-1c8c72c50523, username: testuser)

    teste2@rumo.com / senha12345 (id: 01a0f9c4-0552-721d-90ea-e7b0ff9af1e1, username: teste2)

    User1 segue User2 (verificar — pode ter sido desfeito nos testes)

    User2 tem 2 atividades "Corrida do user2" (7000m, 2400s, 450 kcal)

    User1 tem 1 atividade "Corrida matinal" (5000m, 1800s, 320 kcal)

    Activity do user2 usada em testes de comments: 01a0f9d8-8431-7d78-a943-bc832533454c

    GPX de teste em backend/samples/sample_run.gpx (2345 pontos, ~7.3km caminhada, "Caminhada vespertina")

Produção (Neon):

    prod@rumo.com / senha12345 (criado no smoke test do Bloco 11, username: produser)

Armadilhas conhecidas (CRÍTICO)
Backend / Python

    bcrypt==4.0.1 obrigatório (4.1+ quebra passlib)

    greenlet==3.1.1 explícito no requirements (Python 3.13 não instala)

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso, sempre conferir no \d tabela se aparece timestamp with time zone

    include_router sem prefix + @router.post("") = FastAPIError: Prefix and path cannot be both empty. Sempre ter prefix no include_router OU caminhos completos nos decorators

    ResponseValidationError com <exception str() failed> — o FastAPI mascara o erro real do Pydantic. Debugar com TypeAdapter + validate_python direto no Python

    selectinload obrigatório quando o schema Pydantic acessa obj.relacao em async (senão MissingGreenlet)

    validation_alias no Pydantic para mapear nome de atributo ORM diferente do nome do campo JSON (ex: author = Field(validation_alias="user"))

    relationship cross-model com TYPE_CHECKING — usar from typing import TYPE_CHECKING + if TYPE_CHECKING: from app.models.x import X para dar type hint sem import circular em runtime

    Swagger pré-preenche campos opcionais Form() com "string" literal — se o usuário não apagar o placeholder, o backend recebe "string" como valor real. Solução: validação defensiva no service (if value == "string": value = None)

    pip install fora da venv ativa cai no Python global. Sempre cd D:\Rumo\backend + .venv\Scripts\Activate.ps1 antes. Se (.venv) não aparecer no prompt, não está ativa

Banco / PostGIS

    Alembic + PostGIS: filtro include_object no env.py

    Migração com Geometry: adicionar import geoalchemy2 no topo E remover op.create_index do GIST

    WKT LINESTRING: ordem é (lon lat). Ex: LINESTRING(-46.63 -23.55, -46.64 -23.56)

    PostGIS + JSONB redundantes — route e raw_track_points guardam os mesmos pontos em formatos diferentes. Decisão: manter ambos. Sempre conferir ST_NPoints(route) == jsonb_array_length(raw_track_points)

    Diferença dev/prod: Docker roda PG 16.4 + PostGIS 3.4; Neon roda PG 17.11 + PostGIS 3.5. Se bug geo não reproduzir local, suspeitar disso primeiro

Neon

    PostGIS NÃO vem habilitado por padrão — precisa rodar CREATE EXTENSION IF NOT EXISTS postgis; no SQL Editor

    Postgres 18 NÃO tem PostGIS ainda no Neon — usar 17

    Duas connection strings: Pooled (host com -pooler) vs Direct (sem -pooler). Usar Direct com asyncpg

    Formato pra asyncpg: postgresql+asyncpg:// (não postgresql://), ssl=require (não sslmode), sem channel_binding=require

    A URL que o Neon dá na UI tem sslmode e channel_binding — precisa editar na mão

    Se a senha tiver caractere especial (@, :, /, #, ?, &, %), precisa URL-encoding. Senhas geradas pelo Neon geralmente são alfanuméricas, mas conferir

Render

    Blueprint vs Website: usar Blueprint (lê o render.yaml). Website cria serviço do zero, ignora o YAML

    Free tier dorme após 15 min sem tráfego. Primeira request demora ~30-50s. Não é bug

    rootDir: backend no render.yaml — sem isso, o Render não acha o requirements.txt nem o alembic.ini

    startCommand com alembic upgrade head && — idempotente, roda toda vez que o serviço reinicia

    DATABASE_URL com sync: false — não vai pro Git, você cola no painel

    SECRET_KEY com generateValue: true — Render gera nova, diferente da local. JWTs não intercambiáveis dev/prod

Ambiente / tooling

    .env nunca commitado. .env local aponta pro Docker, env var do Render aponta pro Neon. Nunca cruzar

    Docker Desktop PRECISA estar aberto — só ter o docker CLI no PATH não basta. ConnectionRefusedError: [WinError 1225] ou failed to connect to the docker API at npipe significa que o Docker Desktop não subiu

    docker compose start (não up -d) se os containers já existem. docker compose down -v NUNCA (apaga volume = apaga dados)

    Errno 10061 Connect call failed ('127.0.0.1', 5432) = Postgres local não está rodando. Subir Docker + docker compose start

    Uvicorn precisa estar rodando em terminal separado — "Impossível conectar-se ao servidor remoto" significa uvicorn down, não bug

    _scratch/ no .gitignore — pasta de scripts descartáveis. VS Code mostra esses arquivos acinzentados (comportamento esperado, não é bug). Nunca versionar (senhas podem aparecer)

    PowerShell mostra UTF-8 como Latin-1 — dado íntegro no banco pode aparecer corrompido no terminal. Confirmar no psql antes de sair caçando bug de encoding

    Ordem de rotas no router: estáticas antes das dinâmicas

    Pylance "X is not accessed" → import não usado, limpar mas não é erro de runtime

Convenções

    Comentários/docstrings em português; nomes em inglês

    REST com prefixos, response_model sempre

    HTTPException: 401 (auth), 403 (permissão), 404 (not found), 409 (conflito), 422 (Pydantic), 400 (bad request)

    Commits em português, padrão feat:, fix:, chore:, docs:

    Blocos incrementais: implementar → testar → commitar

    Usuário prefere explicações didáticas com o "porquê"

    Sempre avisar quando estiver perto do limite de contexto e gerar handoff

Estilo de comunicação preferido

Direto ao ponto, blocos de código prontos para copiar/colar, explicações concisas. Sempre avisar quando estiver perto do limite de contexto.