# Rumo — Handoff Atualizado (após Bloco 12)

## Sobre o projeto
Sistema de monitoramento de exercícios físicos (tipo Strava). Nome: **Rumo**.
Usuário: iniciante em Python/backend, experiente em JS (2 sistemas em produção).
Objetivo: produção real.

## Stack
- **Backend:** Python 3.13.7 + FastAPI + SQLAlchemy 2.0 async + Alembic + GeoAlchemy2
- **Banco dev:** PostgreSQL 16 + PostGIS 3.4 (Docker)
- **Banco prod:** Neon (PostGIS habilitado)
- **Cache:** Redis (Docker)
- **Deploy backend:** Render | **Frontend:** Vercel (React, futuro) | **Mobile:** Flutter (futuro)
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

## Estrutura de pastas

D:\Rumo
├── .gitignore, README.md, docker-compose.yml
├── docs\HANDOFF.md
├── backend
│ ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
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
- `POST /activities/upload` — 201 (multipart, arquivo `.gpx`, parse + cálculo automático) ← **NOVO no Bloco 12**
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

## Blocos concluídos
✅ 1 a 9 (ver histórico)
✅ 10a - Follows (tabela, endpoints de seguir/deixar de seguir/listar)
✅ 10b - Feed (atividades próprias + de quem segue, com autor enriquecido)
✅ 10c - Likes (curtir/descurtir/listar, idempotente)
✅ 10d - Comentários (criar/listar/deletar, 403 pra não-autor, ForbiddenError criado)
✅ 12 - Upload GPX + cálculo automático de métricas (parser, Haversine, elevação, PostGIS + JSONB, refatoração do activity_service)

## Blocos pendentes
⏳ 11 - Deploy Render + Neon (PRÓXIMO)
⏳ 12b - Upload FIT (opcional, formato binário com fitdecode/garmin-fit-sdk)
⏳ 13 - Frontend React (Vercel)
⏳ 14 - Mobile Flutter

## Pendências técnicas (dívida para limpar)
1. **`calories` fica NULL no upload GPX** — cálculo precisa de peso + FC + tipo, é bloco separado.
2. **Sem upload de foto de atividade** — precisa de storage (S3/Cloudinary/R2).
3. **Sem rate limiting** — abuso de API é trivial.
4. **Redis não está sendo usado** (está no docker-compose mas não tem cache de feed/stats).
5. **Sem testes automatizados** — `tests/` ainda vazia.
6. **`UserResponse` expõe `email` e `birth_date`** — usado só em `/auth/me` (ok), mas vale revisar antes de prod.
7. **`GET /activities/{id}/comments` exige auth** — se quiser público depois, remover `Depends(get_current_user)`.
8. **Não há `/activities/{id}/route` ou `/track`** — o `ActivityResponse` não expõe `route` nem `raw_track_points` (decisão de performance). Se o frontend precisar desenhar o mapa, criar endpoint dedicado que retorna a geometria.

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

# Banco
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "\d activities"
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "\d comments"
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "SELECT id, title, activity_type, distance_m, ST_NPoints(route) AS n_points FROM activities ORDER BY created_at DESC LIMIT 5;"

# Testar parser GPX isolado (sem API)
python -c "from app.services.gpx_service import parse_gpx; d = parse_gpx(open('samples/sample_run.gpx','rb').read()); print(d)"

# Git
cd D:\Rumo ; git add . ; git commit -m "..." ; git push

Usuários de teste

    teste@rumo.com / senha12345 (id: 01a0f49c-8e6d-7506-a1c1-1c8c72c50523, username: testuser)

    teste2@rumo.com / senha12345 (id: 01a0f9c4-0552-721d-90ea-e7b0ff9af1e1, username: teste2)

    User1 segue User2 (verificar — pode ter sido desfeito nos testes)

    User2 tem 2 atividades "Corrida do user2" (7000m, 2400s, 450 kcal)

    User1 tem 1 atividade "Corrida matinal" (5000m, 1800s, 320 kcal)

    Activity do user2 usada em testes de comments: 01a0f9d8-8431-7d78-a943-bc832533454c

    GPX de teste em backend/samples/sample_run.gpx (2345 pontos, ~7.3km caminhada, "Caminhada vespertina")

    Última atividade de teste criada via upload: apagada no fim do Bloco 12 (banco de dev limpo)

    Armadilhas conhecidas (CRÍTICO)

    bcrypt==4.0.1 obrigatório

    greenlet explícito no requirements

    Alembic + PostGIS: filtro include_object no env.py

    Migração com Geometry: adicionar import geoalchemy2 no topo E remover op.create_index do GIST

    WKT LINESTRING: ordem é (lon lat). Ex: LINESTRING(-46.63 -23.55, -46.64 -23.56)

    .env nunca commitado

    Venv sempre ativado antes de trabalhar — o erro Could not load module '.venv' significa que você está fora da pasta do projeto

    Datas sempre UTC

    docker compose start antes de subir uvicorn após reiniciar PC

    Nunca docker compose down -v

    Uvicorn precisa estar rodando em terminal separado — "Impossível conectar-se ao servidor remoto" significa uvicorn down, não bug

    Ordem de rotas no router: estáticas antes das dinâmicas

    Pylance "X is not accessed" → import não usado, limpar mas não é erro de runtime

        Pylance "X is not accessed" → import não usado, limpar mas não é erro de runtime

    uuid.uuid7 NÃO existe no Python 3.13 — usar from uuid6 import uuid7

    DateTime sem timezone=True — bug silencioso, sempre conferir no \d tabela se aparece timestamp with time zone

    include_router sem prefix + @router.post("") = FastAPIError: Prefix and path cannot be both empty. Sempre ter prefix no include_router OU caminhos completos nos decorators

    ResponseValidationError com <exception str() failed> — o FastAPI mascara o erro real do Pydantic. Debugar com TypeAdapter + validate_python direto no Python

    selectinload obrigatório quando o schema Pydantic acessa obj.relacao em async (senão MissingGreenlet)

    validation_alias no Pydantic para mapear nome de atributo ORM diferente do nome do campo JSON (ex: author = Field(validation_alias="user"))

    PowerShell mostra UTF-8 como Latin-1 — dado íntegro no banco pode aparecer corrompido no terminal. Confirmar no psql antes de sair caçando bug de encoding

    Docker Desktop PRECISA estar aberto — só ter o docker CLI no PATH não basta. ConnectionRefusedError: [WinError 1225] ou failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine significa que o Docker Desktop não subiu. Abrir, esperar ficar verde na bandeja, depois docker compose start

    relationship cross-model com TYPE_CHECKING — usar from typing import TYPE_CHECKING + if TYPE_CHECKING: from app.models.x import X para dar type hint sem import circular em runtime. Evita warning do Pylance sem quebrar nada

    Swagger pré-preenche campos opcionais Form() com "string" literal — se o usuário não apagar o placeholder, o backend recebe "string" como valor real (bug silencioso que só explode no commit). Solução: validação defensiva no service (if value == "string": value = None). Descoberto no Bloco 12.

    pip install fora da venv ativa cai no Python global (Defaulting to user installation because normal site-packages is not writeable). Sempre cd D:\Rumo\backend + .venv\Scripts\Activate.ps1 antes. Se (.venv) não aparecer no prompt, não está ativa.

    PostGIS + JSONB redundantes — route e raw_track_points guardam os mesmos pontos em formatos diferentes (LINESTRING vs JSONB). Decisão: manter ambos (route pra queries geográficas, JSONB pra reprocessar métricas depois). Sempre conferir ST_NPoints(route) == jsonb_array_length(raw_track_points).

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
Como retomar no próximo chat

Mensagem sugerida:

    Continuando o projeto Rumo. Aqui está o handoff (após Bloco 12). Bora para o Bloco 11 — Deploy Render + Neon. Gostaria de seguir nesta pegando quando o chat estiver próximo do limite, gerar um Handoff para passar para o próximo chat.

text


---

Salva isso em `docs\HANDOFF.md` e commita:

```powershell
cd D:\Rumo
git add docs/HANDOFF.md
git commit -m "docs: atualiza handoff apos Bloco 12"
git push

Pronto. Agora você pode abrir o chat novo com segurança. Cola o handoff + a mensagem sugerida e bora pro Bloco 11 — Deploy Render + Neon. 🚀

## Visão do produto (NORTE — ler antes de qualquer decisão)

**Rumo é um app de exercício físico ambicioso, semelhante ao Strava.** Não é
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
