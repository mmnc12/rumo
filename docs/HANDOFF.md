# Rumo — Handoff Atualizado (após Bloco 9)

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
2. IDs UUID v7 (lib `uuid6`)
3. PostGIS desde o início (rotas GPS como LINESTRING SRID 4326)
4. Config via `.env` + Pydantic Settings — `.env` NUNCA versionado
5. Alembic com filtro `include_object` (ignora tabelas de sistema PostGIS)
6. **`bcrypt==4.0.1` fixado** (4.1+ quebra passlib)
7. **`greenlet==3.1.1` explícito** no requirements (Python 3.13 não instala)
8. Ao gerar migração com `Geometry`: adicionar `import geoalchemy2` no topo E remover `op.create_index` do índice GIST (PostGIS cria automaticamente)
9. Senhas com bcrypt, JWT HS256, `get_current_user` como dependência reutilizável
10. Modelo `Activity` opção A: `route` LINESTRING + `raw_track_points` JSONB (sem tabela TrackPoint separada por enquanto)
11. **Ordem de rotas no router:** rotas estáticas (`/stats/...`) declaradas ANTES das dinâmicas (`/{id}`) para o FastAPI não tentar parsear "stats" como UUID
12. **Pace/velocidade no summary são ponderados** (soma/soma), não média de médias. Retornam `null` quando divisor é zero.

## Estrutura de pastas
```
D:\Rumo\
├── .gitignore, README.md, docker-compose.yml
├── docs\HANDOFF.md
├── backend\
│   ├── .env (não versionado), .env.example, requirements.txt, alembic.ini
│   ├── alembic\env.py + versions\{users, activities}
│   ├── app\
│   │   ├── main.py, config.py, database.py
│   │   ├── core\security.py, core\dependencies.py
│   │   ├── models\{user.py, activity.py, __init__.py}
│   │   ├── schemas\{user.py, activity.py, stats.py, __init__.py}
│   │   ├── routers\{auth.py, activities.py, __init__.py}
│   │   └── services\{activity_service.py, stats_service.py, __init__.py}
│   └── tests\
├── mobile\ (vazio)
└── web\ (vazio)
```

## Models existentes
### User
- id (UUID v7), email (unique), username (unique), full_name
- hashed_password, weight_kg, height_cm, birth_date
- is_active, created_at, updated_at

### Activity
- id (UUID v7), user_id (FK users CASCADE)
- activity_type (enum: run/walk/cycle/hike/swim/other)
- title, description
- started_at (indexed), finished_at, duration_s
- distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps
- route (Geometry LINESTRING 4326)
- raw_track_points (JSONB)
- created_at, updated_at
- Índices: user_id, started_at, (user_id+started_at), GIST em route
- Constraints: distance/duration/calories >= 0

## Endpoints existentes
- `GET /` — metadados
- `GET /health` — status API + banco
- `POST /auth/register` — cria usuário (201, 409 se duplicado)
- `POST /auth/login` — form-urlencoded (username=email), retorna JWT
- `GET /auth/me` — protegido, dados do usuário atual
- `POST /activities` — cria atividade (autenticado, 201)
- `GET /activities?limit=20&offset=0` — lista atividades do usuário (paginado)
- `GET /activities/{id}` — detalhes (só do dono, 404 se não for)
- `DELETE /activities/{id}` — remove (204, só do dono)
- `GET /activities/stats/summary?activity_type=` — totais gerais (com filtro opcional por tipo)
- `GET /activities/stats/weekly?weeks=8&activity_type=` — resumo últimas N semanas (1<=weeks<=52)
- `GET /activities/stats/monthly?months=6&activity_type=` — resumo últimos N meses (1<=months<=24)

## Blocos concluídos
✅ 1 - Estrutura + Git + GitHub
✅ 2 - Docker Compose (Postgres/PostGIS + Redis)
✅ 3 - FastAPI + SQLAlchemy async + /health
✅ 4 - Model User + Alembic + 1ª migração
✅ 5 - Schemas + hash + POST /auth/register
✅ 6 - JWT + POST /auth/login + GET /auth/me
✅ 7 - Model Activity + PostGIS + migração
✅ 8 - Schemas + endpoints CRUD de atividades
✅ 9 - Estatísticas (summary, weekly, monthly com filtro por tipo)

## Blocos pendentes
⏳ 10 - Social (follow, feed, likes, comentários) — GRANDE, quebrar em sub-blocos
⏳ 11 - Deploy Render + Neon
⏳ 12 - Frontend React (Vercel)
⏳ 13 - Mobile Flutter

## Próximo passo imediato — Bloco 10 (Social)

Sugestão de quebra em sub-blocos testáveis:
- **10a — Follows:** tabela `follows` (follower_id, following_id, created_at, unique composto, CASCADE). Endpoints: `POST /users/{id}/follow`, `DELETE /users/{id}/follow`, `GET /users/{id}/followers`, `GET /users/{id}/following`. Regras: não seguir a si mesmo, 404 se user não existe, 409 se já segue.
- **10b — Feed:** `GET /feed?limit=20&offset=0` — atividades de quem o usuário segue, ordenado por `started_at DESC`. Considerar join com `follows` ou subquery.
- **10c — Likes:** tabela `likes` (user_id, activity_id, created_at, unique composto, CASCADE). Endpoints: `POST /activities/{id}/like`, `DELETE /activities/{id}/like`, `GET /activities/{id}/likes`. Retornar contagem + flag `liked_by_me`.
- **10d — Comentários:** tabela `comments` (id UUID v7, user_id, activity_id, content, created_at, updated_at, CASCADE). Endpoints: `POST /activities/{id}/comments`, `GET /activities/{id}/comments` (paginado), `DELETE /comments/{id}` (só o autor ou dono da atividade).

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

## Usuário de teste
- `teste@rumo.com` / `senha12345`
- Tem 1 atividade de teste (`run`, 5000m, 1800s, 320 kcal, iniciada em 2026-09-28)

## Armadilhas conhecidas (CRÍTICO)
1. `bcrypt==4.0.1` obrigatório
2. `greenlet` explícito no requirements
3. Alembic + PostGIS: filtro `include_object` no env.py
4. Migração com `Geometry`: adicionar `import geoalchemy2` no topo E remover `op.create_index` do GIST
5. **WKT LINESTRING:** pontos separados por vírgula, coordenadas do mesmo ponto por espaço. Ordem é **(lon lat)**, não (lat lon). Ex: `LINESTRING(-46.63 -23.55, -46.64 -23.56)`
6. `.env` nunca commitado
7. Venv sempre ativado antes de trabalhar
8. Datas sempre UTC
9. `docker compose start` antes de subir uvicorn após reiniciar PC
10. Nunca `docker compose down -v` (apaga volumes)
11. **Uvicorn precisa estar rodando em terminal separado** — se `Invoke-RestMethod` diz "Impossível conectar-se ao servidor remoto", é porque o servidor não está de pé (não é bug do endpoint)
12. **Ordem de rotas no router:** rotas estáticas antes das dinâmicas (senão FastAPI tenta parsear prefixo como UUID → 422)
13. **Pylance reclama de imports não usados** ("X is not accessed") — limpar, mas não é erro de runtime

## Convenções
- Comentários/docstrings em português; nomes em inglês
- REST com prefixos, `response_model` sempre
- HTTPException: 401 (auth), 403 (permissão), 404 (not found), 409 (conflito), 422 (validação Pydantic automática)
- Commits em português, padrão `feat:`, `fix:`, `chore:`, `docs:`
- Blocos incrementais: implementar → testar → commitar
- Usuário prefere explicações didáticas com o "porquê"
- **Sempre avisar quando estiver perto do limite de contexto e gerar handoff**

## Estilo de comunicação preferido
Direto ao ponto, blocos de código prontos para copiar/colar, explicações concisas. Sempre avisar quando estiver perto do limite de contexto.