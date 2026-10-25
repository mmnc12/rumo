"""
Configuração compartilhada de testes do Rumo.

Estratégia:
- Banco: Postgres 16 + PostGIS em Docker (docker-compose.test.yml, porta 5433).
- App: importa o app real (app.main.app) mas NÃO dispara lifespan.
- Sessão:
  * `db_session` — usada pelos testes para setup/asserts diretos.
  * `client` — NÃO reaproveita `db_session`; abre sessão nova por request
    via `test_engine`. Sem isso, a mesma conexão asyncpg é compartilhada
    entre teste e request HTTP, causando "another operation is in progress"
    e "attached to a different loop".
- Auth: sobrescreve get_current_user.
- Isolamento: TRUNCATE ... CASCADE por teste.
- Event loop: loop_scope="session" em todas as fixtures async + NullPool
  no engine. NullPool abre/fecha conexão por uso, então nenhuma conexão
  sobrevive ao loop que a criou.
"""

import os
from pathlib import Path

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://rumo:rumo@localhost:5433/rumo_test"
)

from collections.abc import AsyncGenerator  # noqa: E402

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

from app.core.dependencies import get_current_user  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402


TEST_DATABASE_URL = os.environ["DATABASE_URL"]
SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine():
    """Engine de teste com NullPool — conexão nova por uso, fechada ao final."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _setup_schema(test_engine):
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(
    test_engine, _setup_schema
) -> AsyncGenerator[AsyncSession, None]:
    """Sessão de teste com isolamento via TRUNCATE CASCADE entre testes."""
    async with test_engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE activity_photos, activities, likes, comments, "
                "notifications, follows, users RESTART IDENTITY CASCADE"
            )
        )

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="session")
async def test_user(db_session: AsyncSession) -> User:
    """Usuário de teste já commitado no banco.

    A sessão usada aqui é fechada ao final da fixture. O `client` abaixo
    abre sessão nova por request, então vê o usuário no banco sem
    compartilhar estado transacional com esta `db_session`.
    """
    from uuid6 import uuid7

    user = User(
        id=uuid7(),
        email="test@rumo.com",
        username="testuser",
        hashed_password="x",
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(loop_scope="session")
async def client(
    test_engine, _setup_schema, test_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP com sessão NOVA por request.

    Não depende de `db_session` — isso evita que a conexão asyncpg do
    teste seja reutilizada pela request HTTP, o que causava
    "another operation is in progress" e "attached to a different loop".
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        session_factory = async_sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        async with session_factory() as session:
            yield session

    async def _override_get_current_user() -> User:
        return test_user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def sample_gpx_bytes() -> bytes:
    path = SAMPLES_DIR / "sample_run.gpx"
    assert path.exists(), f"Sample GPX ausente: {path}"
    return path.read_bytes()


@pytest_asyncio.fixture
def sample_fit_bytes() -> bytes:
    path = SAMPLES_DIR / "sample_run.fit"
    assert path.exists(), f"Sample FIT ausente: {path}"
    return path.read_bytes()