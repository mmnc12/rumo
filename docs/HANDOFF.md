# Rumo — Handoff Atualizado (após Bloco 10c)

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
8. Ao gerar migração com `Geometry`: adicionar `import geoalchemy2` no topo E remover `op.create_index` do índice GIST
9. Senhas com bcrypt, JWT HS256, `get_current_user` como dependência reutilizável
10. Modelo `Activity` opção A: `route` LINESTRING + `raw_track_points` JSONB (sem tabela TrackPoint separada)
11. **Ordem de rotas no router:** rotas estáticas (`/stats/...`) declaradas ANTES das dinâmicas (`/{id}`)
12. **Pace/velocidade no summary são ponderados** (soma/soma), não média de médias
13. **`DateTime(timezone=True)` em TODAS as colunas de data/hora** (users, activities, follows, likes)
14. **`activity_service`, `stats_service`, `follow_service`, `like_service` agora usam `ServiceError`** (exceto `activity_service` que ainda usa HTTPException — ver pendência abaixo)
15. **Erros de negócio:** `ServiceError` genérico em `app/services/errors.py` com subclasses `NotFoundError` (404), `ConflictError` (409), `BadRequestError` (400). Routers traduzem `ServiceError` → `HTTPException` via helper.
16. **`lazy="raise"` nos `relationship()`** + `selectinload` explícito nos services que precisam carregar relações (evita `MissingGreenlet` no async)
17. **`FeedItemResponse`** usa `validation_alias="user"` para mapear o ORM `Activity.user` → campo `author` no JSON. Mesmo padrão a ser usado em `CommentResponse`.
18. **Routers de activities com prefixo no `main.py`** (`prefix="/activities"`), então decorators usam `@router.post("")` (sem barra).
19. **`UserPublic`** (sem email/birth_date) para expor dados de outros usuários. `UserResponse` (com email) só para o próprio `/auth/me`.

## Estrutura de pastas
```
D:\Rumo\
├── .gitignore, README.md, docker-compose.yml
├── docs\HANDOFF.md
├── backend\
│   ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│   ├── alembic\env.py + versions\{users, activities, follows, likes}
│   ├── app\
│   │   ├── main.py, config.py, database.py
│   │   ├── core\security.py, core\dependencies.py
│   │   ├── models\{user.py, activity.py, follow.py, like.py, __init__.py}
│   │   ├── schemas\{user.py, activity.py, stats.py, like.py, __init__.py}
│   │   ├── routers\{auth.py, activities.py, feed.py, users.py, __init__.py}
│   │   └── services\{activity_service.py, stats_service.py, follow_service.py, like_service.py, feed_service.py, errors.py, __init__.py}
│   └── tests\
├── mobile\ (vazio)
└── web\ (vazio)
```

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
- route (Geometry LINESTRING 4326), raw_track_points (JSONB)
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
- `POST /activities` — 201
- `GET /activities?limit=20&offset=0` — lista próprias atividades
- `GET /activities/{id}` — detalhes (só do dono)
- `DELETE /activities/{id}` — 204 (só do dono)
- `GET /activities/stats/summary?activity_type=` — totais gerais
- `GET /activities/stats/weekly?weeks=8&activity_type=` — últimas N semanas
- `GET /activities/stats/monthly?months=6&activity_type=` — últimos N meses
- `POST /activities/{id}/like` — 200 `{count, liked_by_me}` (idempotente)
- `DELETE /activities/{id}/like` — 204 (idempotente)
- `GET /activities/{id}/likes?limit&offset` — 200 `{count, liked_by_me, users[]}`

### Feed
- `GET /feed?limit=20&offset=0` — atividades próprias + de quem segue, com `author` (FeedItemResponse)

## Blocos concluídos
✅ 1 a 9 (ver histórico)
✅ 10a - Follows (tabela, endpoints de seguir/deixar de seguir/listar)
✅ 10b - Feed (atividades próprias + de quem segue, com autor enriquecido)
✅ 10c - Likes (curtir/descurtir/listar, idempotente)

## Blocos pendentes
⏳ 10d - Comentários (PRÓXIMO)
⏳ 11 - Deploy Render + Neon
⏳ 12 - Frontend React (Vercel)
⏳ 13 - Mobile Flutter

## Próximo passo imediato — Bloco 10d (Comentários)

**Design já fechado:**

### Tabela `comments`
```
id          UUID v7 (PK)
user_id     UUID FK users CASCADE
activity_id UUID FK activities CASCADE
content     TEXT (limite 500 validado no schema Pydantic)
created_at  timestamptz (DateTime(timezone=True))
updated_at  timestamptz (DateTime(timezone=True), onupdate)
Índices: activity_id, user_id
Sem UNIQUE (pode comentar várias vezes)
```

### Model (`models/comment.py`)
- `user = relationship("User", lazy="raise")` para o selectinload funcionar
- (opcional) `activity = relationship("Activity", lazy="raise")` — não precisa por ora

### Schemas (`schemas/comment.py`)
- `CommentCreate` (input): `content: str` com `min_length=1, max_length=500`
- `CommentResponse` (output): `id, activity_id, content, created_at, updated_at, author: UserPublic`
  - `author: UserPublic = Field(validation_alias="user")` — mesmo padrão do FeedItemResponse
- Não precisa wrapper — endpoints retornam `list[CommentResponse]`

### Service (`services/comment_service.py`)
- `create_comment(db, user_id, activity_id, content)` → dict/obj
  - Valida que activity existe (404)
  - Cria Comment, commit, retorna com `selectinload(user)`
- `list_comments(db, activity_id, limit, offset)` → list[Comment]
  - Valida que activity existe
  - Ordena por `created_at ASC` (mais antigo primeiro — é conversa)
  - `selectinload(Comment.user)`
- `delete_comment(db, user_id, comment_id)`
  - Valida que comment existe (404)
  - Valida que `comment.user_id == user_id` → senão 403 (ForbiddenError precisa ser criado em errors.py)
  - DELETE, commit

### Router novo (`routers/comments.py`)
- `POST /activities/{activity_id}/comments` — 201, retorna CommentResponse
- `GET /activities/{activity_id}/comments?limit&offset` — 200, list[CommentResponse]
- `DELETE /comments/{comment_id}` — 204 (só autor)

**⚠️ Atenção:** os endpoints de POST/GET comments são `/activities/{id}/comments` — precisam ficar em `activities.py` **OU** você pode colocar `prefix="/activities"` no `comments.py` também. Recomendação: criar `routers/comments.py` com **dois routers internos** ou registrar com prefixo diferente para o DELETE. Estratégia mais limpa:
  - `routers/comments.py` define `router = APIRouter()` com `POST /activities/{activity_id}/comments` e `GET /activities/{activity_id}/comments` (caminhos completos) e `DELETE /comments/{comment_id}`
  - `main.py` registra `app.include_router(comments.router, tags=["comments"])` (SEM prefix)

### Migração
- `alembic revision --autogenerate -m "add comments table"`

## Comandos essenciais
```powershell
# Subir infra
cd D:\Rumo ; docker compose start

# Rodar backend (TERMINAL SEPARADO, deixar aberto)
cd D:\Rumo\backend ; .venv\Scripts\Activate.ps1 ; uvicorn app.main:app --reload

# Alembic
alembic current
alembic revision --autogenerate -m "descricao"
alembic upgrade head
alembic downgrade -1

# Banco
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "\d activities"

# Git
cd D:\Rumo ; git add . ; git commit -m "..." ; git push
```

## Usuários de teste
- `teste@rumo.com` / `senha12345` (id: `01a0f49c-8e6d-7506-a1c1-1c8c72c50523`, username: `testuser`)
- `teste2@rumo.com` / `senha12345` (id: `01a0f9c4-0552-721d-90ea-e7b0ff9af1e1`, username: `teste2`)
- User1 segue User2 (verificar — pode ter sido desfeito nos testes)
- User2 tem 2 atividades "Corrida do user2" (7000m, 2400s, 450 kcal)
- User1 tem 1 atividade "Corrida matinal" (5000m, 1800s, 320 kcal)
- Likes existentes: pode ou não ter (depende dos testes)

## Armadilhas conhecidas (CRÍTICO)
1. `bcrypt==4.0.1` obrigatório
2. `greenlet` explícito no requirements
3. Alembic + PostGIS: filtro `include_object` no env.py
4. Migração com `Geometry`: adicionar `import geoalchemy2` no topo E remover `op.create_index` do GIST
5. **WKT LINESTRING:** ordem é (lon lat). Ex: `LINESTRING(-46.63 -23.55, -46.64 -23.56)`
6. `.env` nunca commitado
7. Venv sempre ativado antes de trabalhar
8. Datas sempre UTC
9. `docker compose start` antes de subir uvicorn após reiniciar PC
10. Nunca `docker compose down -v`
11. **Uvicorn precisa estar rodando em terminal separado** — "Impossível conectar-se ao servidor remoto" significa uvicorn down, não bug
12. **Ordem de rotas no router:** estáticas antes das dinâmicas
13. **Pylance "X is not accessed"** → import não usado, limpar mas não é erro de runtime
14. **`uuid.uuid7` NÃO existe no Python 3.13** — usar `from uuid6 import uuid7`
15. **`DateTime` sem `timezone=True`** — bug silencioso, sempre conferir no `\d tabela` se aparece `timestamp with time zone`
16. **`include_router` sem prefix + `@router.post("")`** = `FastAPIError: Prefix and path cannot be both empty`. Sempre ter prefix no `include_router` OU barra nos decorators
17. **`ResponseValidationError` com `<exception str() failed>`** — o FastAPI mascara o erro real do Pydantic. Debugar com `TypeAdapter` + `validate_python` direto no Python
18. **`selectinload` obrigatório** quando o schema Pydantic acessa `obj.relacao` em async (senão `MissingGreenlet`)
19. **`validation_alias` no Pydantic** para mapear nome de atributo ORM diferente do nome do campo JSON (ex: `author = Field(validation_alias="user")`)
20. **PowerShell mostra UTF-8 como Latin-1** — dado íntegro no banco pode aparecer corrompido no terminal. Confirmar no psql antes de sair caçando bug de encoding

## Pendências técnicas (dívida para limpar depois)
1. **`activity_service.py` ainda usa `HTTPException`** diretamente. Refatorar para usar `ServiceError` como os outros services. Os endpoints de `/activities/{id}` (get/delete) já têm `try/except ServiceError`, mas não funcionam se o service não levanta `ServiceError`. Verificar e refatorar no Bloco 11 ou num bloco de limpeza.
2. **Sem `ForbiddenError` em `errors.py` ainda** — vai ser necessário no 10d (403 para deletar comentário de outro user). Criar.
3. **`UserResponse` expõe `email` e `birth_date`** — usado só em `/auth/me` (ok), mas vale revisar antes de prod.

## Convenções
- Comentários/docstrings em português; nomes em inglês
- REST com prefixos, `response_model` sempre
- HTTPException: 401 (auth), 403 (permissão), 404 (not found), 409 (conflito), 422 (Pydantic)
- Commits em português, padrão `feat:`, `fix:`, `chore:`, `docs:`
- Blocos incrementais: implementar → testar → commitar
- Usuário prefere explicações didáticas com o "porquê"
- **Sempre avisar quando estiver perto do limite de contexto e gerar handoff**

## Estilo de comunicação preferido
Direto ao ponto, blocos de código prontos para copiar/colar, explicações concisas. Sempre avisar quando estiver perto do limite de contexto.

## Como retomar no próximo chat
Mensagem sugerida:
> Continuando o projeto Rumo. Aqui está o handoff (após Bloco 10c). Bora para o Bloco 10d — Comentários. Gostaria de seguir nesta pegando quando o chat estiver próximo do limite, gerar um Handoff para passar para o próximo chat.