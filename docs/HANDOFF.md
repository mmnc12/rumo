# Rumo — Resumo de Handoff

## Sobre o projeto
Sistema de monitoramento de exercícios físicos (caminhada, corrida, etc.) semelhante ao Strava.
Nome do projeto: **Rumo**
Usuário: desenvolvedor iniciante em Python/backend, mas com experiência em JS e dois sistemas em produção.
Objetivo: colocar em produção real.

## Stack decidida
- **Backend:** Python 3.13.7 + FastAPI + SQLAlchemy 2.0 (async) + Alembic
- **Banco dev:** PostgreSQL 16 + PostGIS 3.4 (Docker Compose local)
- **Banco prod:** Neon (PostgreSQL + PostGIS, free tier, sem pausa por inatividade)
- **Cache:** Redis 7 (Docker local em dev; Upstash em prod se necessário)
- **Frontend (futuro):** React + Vite (deploy no Vercel)
- **Mobile (futuro):** Flutter
- **Deploy backend:** Render
- **IDE:** VS Code
- **Repositório:** https://github.com/mmnc12/rumo (privado)

## Decisões de arquitetura importantes
1. **Async em tudo** — FastAPI, SQLAlchemy, Alembic usam `async`/`await`. Driver: `asyncpg`.
2. **IDs em UUID v7** — gerados em Python com a lib `uuid6`. Motivo: segurança, ordenável por tempo, ideal para mobile/offline sync.
3. **PostGIS desde o início** — para armazenar rotas GPS como `LINESTRING`.
4. **Config via `.env`** com Pydantic Settings. `.env` NUNCA vai para o Git (está no `.gitignore`).
5. **Alembic com filtro `include_object`** em `alembic/env.py` — ignora tabelas do PostGIS (schema `tiger`, `topology`, `public.spatial_ref_sys`, etc.) para não tentar dropá-las.
6. **bcrypt fixado em 4.0.1** — versões 4.1+ são incompatíveis com passlib. Sempre instalar `bcrypt==4.0.1`.
7. **greenlet** — precisa estar explícito no `requirements.txt` (SQLAlchemy async depende).
8. **Senhas com bcrypt** — `hash_password()` e `verify_password()` em `core/security.py`.
9. **JWT com HS256** — `create_access_token()` e `decode_access_token()`. `SECRET_KEY` gerada com `secrets.token_urlsafe(64)`.
10. **Proteção de rotas** com `get_current_user` — dependência em `core/dependencies.py`.
11. **`response_model`** sempre em endpoints que retornam dados de usuário, para filtrar `hashed_password` automaticamente.
12. **Commits em português**, no padrão convencional (`feat:`, `chore:`, `fix:`).

## Estrutura de pastas atual
```
D:\Rumo\
├── .gitignore
├── README.md
├── docker-compose.yml          # postgis/postgis:16-3.4 + redis:7-alpine
├── docs\
│   └── HANDOFF.md              # este arquivo
├── backend\
│   ├── .env                    # NÃO versionado
│   ├── .env.example            # versionado
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic\
│   │   ├── env.py              # modificado (async + filtro PostGIS)
│   │   └── versions\
│   │       └── 8bd034e3e802_cria_tabela_users.py
│   ├── app\
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI + lifespan + /health + include_router(auth)
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── database.py         # engine async + AsyncSessionLocal + Base + get_db
│   │   ├── core\
│   │   │   ├── __init__.py
│   │   │   ├── security.py     # hash_password, verify_password, create_access_token, decode_access_token
│   │   │   └── dependencies.py # oauth2_scheme, get_current_user
│   │   ├── models\
│   │   │   ├── __init__.py     # exporta User
│   │   │   └── user.py         # User (id UUID v7, email, username, full_name, hashed_password, weight_kg, height_cm, birth_date, is_active, created_at, updated_at)
│   │   ├── schemas\
│   │   │   ├── __init__.py     # exporta UserCreate, UserLogin, UserResponse
│   │   │   └── user.py
│   │   ├── routers\
│   │   │   ├── __init__.py     # exporta auth
│   │   │   └── auth.py         # POST /auth/register, POST /auth/login, GET /auth/me
│   │   └── services\
│   │       └── __init__.py
│   └── tests\
├── mobile\                     # vazio (Flutter, futuro)
└── web\                        # vazio (React, futuro)
```

## Comandos úteis (Windows PowerShell)

### Subir/parar infra
```powershell
cd D:\Rumo
docker compose start        # Iniciar containers (preserva dados)
docker compose stop         # Parar containers (preserva dados)
docker compose up -d        # Subir containers (primeira vez ou após down)
docker compose ps           # Ver status
# ⚠️ NUNCA rodar "docker compose down -v" — apaga os dados
```

### Rodar backend
```powershell
cd D:\Rumo\backend
.venv\Scripts\Activate.ps1     # Ativar venv (sempre antes de trabalhar)
uvicorn app.main:app --reload   # Rodar servidor em http://localhost:8000
```

### Alembic
```powershell
alembic current                                    # Ver migração aplicada
alembic revision --autogenerate -m "descricao"     # Gerar migração
alembic upgrade head                               # Aplicar
alembic downgrade -1                               # Reverter última
```

### Postgres via Docker
```powershell
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "\dt"
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "SELECT * FROM users;"
docker exec -it rumo-postgres psql -U rumo -d rumo_dev -c "\d users"
```

### Git
```powershell
cd D:\Rumo
git status
git add .
git commit -m "feat: descricao"
git push
```

## Credenciais de desenvolvimento (locais)
- **Postgres:** `postgresql+asyncpg://rumo:rumo_dev_password@localhost:5432/rumo_dev`
- **Redis:** `redis://localhost:6379/0`
- **Usuário de teste criado:** `teste@rumo.com` / `senha12345`

## Blocos concluídos
- ✅ **Bloco 1** — Estrutura de pastas + Git + GitHub
- ✅ **Bloco 2** — Docker Compose (Postgres/PostGIS + Redis)
- ✅ **Bloco 3** — FastAPI + SQLAlchemy async + `/` e `/health`
- ✅ **Bloco 4** — Model `User` + Alembic + primeira migração
- ✅ **Bloco 5** — Schemas Pydantic + hash bcrypt + `POST /auth/register`
- ✅ **Bloco 6** — JWT + `POST /auth/login` + `GET /auth/me`

## Blocos pendentes (roadmap)
- ⏳ **Bloco 7** — Model `Activity` + `TrackPoint` (com PostGIS LINESTRING) + migração
- ⏳ **Bloco 8** — Endpoints de atividades (criar, listar, detalhes, deletar)
- ⏳ **Bloco 9** — Estatísticas (pace, calorias, distância acumulada)
- ⏳ **Bloco 10** — Social (follow, feed, likes, comentários)
- ⏳ **Bloco 11** — Deploy no Render + Neon + variáveis de ambiente
- ⏳ **Bloco 12** — Frontend React (Vercel)
- ⏳ **Bloco 13** — App Flutter

## Armadilhas conhecidas (importantes)
1. **`bcrypt==4.0.1` obrigatório** — versões novas quebram o passlib com `AttributeError: module 'bcrypt' has no attribute '__about__'` ou `ValueError: password cannot be longer than 72 bytes`.
2. **`greenlet` deve estar explícito no `requirements.txt`** — SQLAlchemy async depende dele mas Python 3.13 não instala automaticamente.
3. **Alembic e PostGIS** — sem o filtro `include_object` no `env.py`, o Alembic tenta dropar dezenas de tabelas de sistema do PostGIS.
4. **`.env` nunca commitado** — verificar `git status` antes de cada commit.
5. **Venv sempre ativado** — o prompt deve mostrar `(.venv)`. Se não aparecer, `.venv\Scripts\Activate.ps1` primeiro.
6. **Async em tudo** — não misturar sync/async no SQLAlchemy.
7. **Datas sempre em UTC** — usar `datetime.now(timezone.utc)`, nunca `datetime.now()`.
8. **Sempre rodar `docker compose start` antes de subir o uvicorn** após reiniciar o PC.

## Próximo passo imediato
**Bloco 7 — Criar models `Activity` e `TrackPoint`:**
- `Activity`: id (UUID v7), user_id (FK), activity_type (enum: run/walk/cycle), started_at, finished_at, distance_m, duration_s, calories, avg_pace, elevation_gain_m, route (PostGIS LINESTRING), title, description, created_at
- `TrackPoint`: id, activity_id (FK), lat, lon, altitude, timestamp (para registrar pontos individuais; opcional no MVP, pode usar só o LINESTRING da Activity)
- Migração Alembic (lembrar do filtro `include_object`)
- Índices: `user_id`, `started_at`

## Convenções de código
- Comentários e docstrings em português
- Nomes de variáveis/funções/classes em inglês
- Endpoints REST com prefixos (`/auth/*`)
- Erros com `HTTPException` (401 para auth, 403 para permissão, 404 para não encontrado, 409 para conflito, 422 é automático do Pydantic)
- `response_model` sempre que retornar dados de usuário

## Sobre a conversa
Este projeto é desenvolvido em blocos incrementais. Cada bloco termina com:
1. Testes funcionando
2. Commit + push
3. Confirmação do usuário

**Ao retomar:** ler este arquivo, verificar se o Docker está rodando, ativar o venv, e perguntar ao usuário em qual bloco parou. O usuário prefere explicações didáticas com o "porquê" das decisões, não apenas comandos prontos.

**Estilo de comunicação preferido:** direto ao ponto, com blocos de código prontos para copiar/colar, explicações concisas, sem enrolação. Sempre avisar quando estiver perto do limite de contexto da conversa.