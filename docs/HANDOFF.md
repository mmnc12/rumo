# Rumo — Handoff Atualizado (após Bloco 10d)

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
13. **`DateTime(timezone=True)` em TODAS as colunas de data/hora**
14. **`ServiceError` genérico** em `app/services/errors.py` com subclasses `NotFoundError` (404), `ConflictError` (409), `BadRequestError` (400), **`ForbiddenError` (403)** (novo no 10d). Routers traduzem `ServiceError` → `HTTPException` via helper.
15. **`lazy="raise"` nos `relationship()`** + `selectinload` explícito nos services que precisam carregar relações
16. **`FeedItemResponse` e `CommentResponse`** usam `validation_alias="user"` para mapear o ORM `*.user` → campo `author` no JSON.
17. **Routers de activities com prefixo no `main.py`** (`prefix="/activities"`), então decorators usam `@router.post("")` (sem barra).
18. **Router de comments SEM prefixo** — paths completos nos decorators (`/activities/{id}/comments` e `/comments/{id}`), registrado sem prefix em `main.py`.
19. **`UserPublic`** (sem email/birth_date) para expor dados de outros usuários. `UserResponse` (com email) só para o próprio `/auth/me`.

## Estrutura de pastas

D:\Rumo
├── .gitignore, README.md, docker-compose.yml
├── docs\HANDOFF.md
├── backend
│ ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│ ├── alembic\env.py + versions{users, activities, follows, likes, comments}
│ ├── app
│ │ ├── main.py, config.py, database.py
│ │ ├── core\security.py, core\dependencies.py
│ │ ├── models{user.py, activity.py, follow.py, like.py, comment.py, init.py}
│ │ ├── schemas{user.py, activity.py, stats.py, like.py, comment.py, init.py}
│ │ ├── routers{auth.py, activities.py, feed.py, users.py, comments.py, init.py}
│ │ └── services{activity_service.py, stats_service.py, follow_service.py, like_service.py, feed_service.py, comment_service.py, errors.py, init.py}
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

### Comment (novo no 10d)
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

### Comments (novo no 10d)
- `POST /activities/{activity_id}/comments` — 201, `CommentResponse` com `author: UserPublic`
- `GET /activities/{activity_id}/comments?limit&offset` — 200, `list[CommentResponse]` (ordem ASC)
- `DELETE /comments/{comment_id}` — 204 (só autor; 403 se não for)

### Feed
- `GET /feed?limit=20&offset=0` — atividades próprias + de quem segue, com `author` (FeedItemResponse)

## Blocos concluídos
✅ 1 a 9 (ver histórico)
✅ 10a - Follows
✅ 10b - Feed
✅ 10c - Likes
✅ 10d - Comentários (criar/listar/deletar, 403 pra não-autor, ForbiddenError criado)

## Blocos pendentes
⏳ 11 - Deploy Render + Neon (PRÓXIMO)
⏳ 12 - Frontend React (Vercel)
⏳ 13 - Mobile Flutter

## Pendências técnicas (dívida para limpar)
1. **`activity_service.py` ainda usa `HTTPException`** diretamente. Refatorar para usar `ServiceError` como os outros services. Verificar se os endpoints `/activities/{id}` (get/delete) realmente funcionam com `try/except ServiceError` — se o service ainda levanta `HTTPException`, o except não pega. Refatorar no Bloco 11 ou num bloco de limpeza.
2. **`UserResponse` expõe `email` e `birth_date`** — usado só em `/auth/me` (ok), mas vale revisar antes de prod.
3. **`GET /activities/{id}/comments` exige auth** — se quiser público depois, remover `Depends(get_current_user)`.

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

# Git
cd D:\Rumo ; git add . ; git commit -m "..." ; git push