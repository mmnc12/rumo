"""Testes do endpoint GET /feed (Sessão 36).

Motivação:
- O /feed nunca teve teste dedicado (buraco desde a S10).
- O S35a passou batido porque não havia teste verificando que o
  autor é exposto no payload. O mobile lê `user`, mas o schema só
  expunha `author`.
- A S36 adiciona `user` ao lado de `author` no FeedItemResponse.
  Estes testes travam o contrato: se alguém remover `user`, o teste
  falha; se alguém remover `author`, o web quebra — o teste também
  falha (regressão dupla).

Padrão: @pytest.mark.asyncio sem scope; helper _make_user e
_make_activity locais (mesmo padrão de test_like.py / test_follow.py)
para não acoplar ao activity_service. Fixtures do conftest.py.
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from app.models.activity import Activity, ActivityType
from app.models.user import User
from app.services import follow_service


def _dt(y: int, m: int, d: int, h: int = 10) -> datetime:
    return datetime(y, m, d, h, 0, 0, tzinfo=timezone.utc)


async def _make_user(
    db_session: AsyncSession, username: str, email: str | None = None
) -> User:
    user = User(
        id=uuid7(),
        username=username,
        email=email or f"{username}@rumo.com",
        hashed_password="x",
        full_name=username.title(),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _make_activity(
    db_session: AsyncSession,
    owner: User,
    activity_type: ActivityType = ActivityType.RUN,
    started_at: datetime | None = None,
    title: str | None = None,
) -> Activity:
    """Cria Activity mínimo (campos NOT NULL sem default)."""
    activity = Activity(
        id=uuid7(),
        user_id=owner.id,
        activity_type=activity_type,
        started_at=started_at or _dt(2026, 1, 5),
        title=title,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity


# ===== Casos base =====


@pytest.mark.asyncio
async def test_feed_empty_for_new_user(
    client, test_user: User
) -> None:
    """Usuário sem atividades e sem follows → feed vazio."""
    r = await client.get("/feed")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_feed_returns_own_activity(
    client, test_user: User, db_session: AsyncSession
) -> None:
    """Atividade própria aparece no feed."""
    act = await _make_activity(db_session, test_user, title="Minha corrida")

    r = await client.get("/feed")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["id"] == str(act.id)
    assert body[0]["title"] == "Minha corrida"


# ===== Contrato do FeedItemResponse (Sessão 36) =====


@pytest.mark.asyncio
async def test_feed_item_has_author(
    client, test_user: User, db_session: AsyncSession
) -> None:
    """Regressão web: `author` continua presente (FeedItem.tsx lê)."""
    await _make_activity(db_session, test_user)

    r = await client.get("/feed")
    assert r.status_code == 200
    item = r.json()[0]
    assert "author" in item, "Campo `author` sumiu — web quebra"
    assert item["author"] is not None
    assert item["author"]["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_feed_item_has_user(
    client, test_user: User, db_session: AsyncSession
) -> None:
    """Sessão 36: `user` presente (Activity.fromJson do mobile lê)."""
    await _make_activity(db_session, test_user)

    r = await client.get("/feed")
    assert r.status_code == 200
    item = r.json()[0]
    assert "user" in item, "Campo `user` sumiu — mobile cai em 'Usuário' e onAuthorTap bloqueia"
    assert item["user"] is not None
    assert item["user"]["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_feed_item_author_and_user_are_same_person(
    client, test_user: User, db_session: AsyncSession
) -> None:
    """`author` e `user` apontam para o MESMO usuário (o dono da atividade).

    Ambos são populados via validation_alias="user" no mesmo
    Activity.user do ORM. Se um dia divergirem, o teste avisa.
    """
    other = await _make_user(db_session, "other_feed1")
    act = await _make_activity(db_session, other, title="Do other")

    r = await client.get("/feed")
    assert r.status_code == 200
    # test_user não segue other → não aparece. Segue pra ver.
    await follow_service.follow_user(db_session, test_user.id, other.id)

    r = await client.get("/feed")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    item = body[0]
    assert item["id"] == str(act.id)
    assert item["author"]["id"] == str(other.id)
    assert item["user"]["id"] == str(other.id)
    assert item["author"]["id"] == item["user"]["id"]
    assert item["author"]["username"] == "other_feed1"
    assert item["user"]["username"] == "other_feed1"


# ===== Follow =====


@pytest.mark.asyncio
async def test_feed_includes_followed_users(
    client, test_user: User, db_session: AsyncSession
) -> None:
    """Atividade de quem o usuário segue aparece no feed."""
    followed = await _make_user(db_session, "followed_feed1")
    act = await _make_activity(db_session, followed, title="Do seguido")
    await follow_service.follow_user(db_session, test_user.id, followed.id)

    r = await client.get("/feed")
    assert r.status_code == 200
    body = r.json()
    ids = {item["id"] for item in body}
    assert str(act.id) in ids


@pytest.mark.asyncio
async def test_feed_excludes_non_followed_users(
    client, test_user: User, db_session: AsyncSession
) -> None:
    """Atividade de quem o usuário NÃO segue não aparece."""
    stranger = await _make_user(db_session, "stranger_feed1")
    act = await _make_activity(db_session, stranger, title="Do estranho")

    r = await client.get("/feed")
    assert r.status_code == 200
    ids = {item["id"] for item in r.json()}
    assert str(act.id) not in ids