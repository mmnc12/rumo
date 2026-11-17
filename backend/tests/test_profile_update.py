"""Testes de PUT /users/me — update parcial do próprio perfil (Sessão 39).

Cobertura:
1. `{}` idempotente — 200, nada muda.
2. Atualiza weight_kg isolado — 200, altura/full_name intactos.
3. Atualiza height_cm isolado — 200, peso intacto.
4. Limpa height_cm com null depois de setar — 200, volta a None.
5. weight_kg fora do range (>500) — 422.
6. Campo proibido (email) — 422 (extra="forbid").
7. Sem Authorization — 401.

O `client` do conftest já autentica como `test_user` via override de
get_current_user. Para o caso 7 é preciso um client SEM o override de
auth, que este arquivo define localmente (`anon_client`).
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_db
from app.main import app


# Client anônimo: só o override de get_db (sem o override de auth do conftest).
# Como get_current_user real depende de OAuth2PasswordBearer (auto_error=True),
# a request sem Authorization é barrada com 401 ANTES do handler.
@pytest_asyncio.fixture(loop_scope="function")
async def anon_client(
    test_engine, _setup_schema, test_user,
) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        session_factory = async_sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    # Intencionalmente NÃO sobrescreve get_current_user.

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ===== Caso 1: payload vazio é idempotente =====
async def test_update_me_empty_payload_is_idempotent(client, test_user):
    resp = await client.put("/users/me", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(test_user.id)
    assert body["weight_kg"] is None
    assert body["height_cm"] is None
    assert body["full_name"] == "Test User"


# ===== Caso 2: atualiza só o peso =====
async def test_update_me_weight_only(client, test_user):
    resp = await client.put("/users/me", json={"weight_kg": 80.0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["weight_kg"] == 80.0
    assert body["height_cm"] is None
    assert body["full_name"] == "Test User"


# ===== Caso 3: atualiza só a altura =====
async def test_update_me_height_only(client, test_user):
    resp = await client.put("/users/me", json={"height_cm": 180.0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["height_cm"] == 180.0
    assert body["weight_kg"] is None
    assert body["full_name"] == "Test User"


# ===== Caso 4: limpa altura com null depois de setar =====
async def test_update_me_clear_height_with_null(client, test_user):
    set_resp = await client.put("/users/me", json={"height_cm": 180.0})
    assert set_resp.status_code == 200
    assert set_resp.json()["height_cm"] == 180.0

    clear_resp = await client.put("/users/me", json={"height_cm": None})
    assert clear_resp.status_code == 200
    assert clear_resp.json()["height_cm"] is None


# ===== Caso 5: peso fora do range =====
async def test_update_me_weight_out_of_range(client, test_user):
    resp = await client.put("/users/me", json={"weight_kg": 600.0})
    assert resp.status_code == 422


# ===== Caso 6: campo proibido (email) =====
async def test_update_me_forbids_email(client, test_user):
    resp = await client.put("/users/me", json={"email": "x@y.com"})
    assert resp.status_code == 422


# ===== Caso 7: sem Authorization =====
async def test_update_me_requires_auth(anon_client):
    resp = await anon_client.put("/users/me", json={"weight_kg": 80.0})
    assert resp.status_code == 401