"""Testes de follow_service (service + rotas HTTP).

Cobre:
- follow_user / unfollow_user (service)
- is_following / following_ids_subquery (service)
- get_followers / get_following (service)
- Rotas /users/{id}/follow (POST/DELETE), /followers, /following

Padrão: datas determinísticas, pytest.approx() para floats, @pytest.mark.asyncio
sem scope (loop_scope herdado de pytest.ini = function).
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow import Follow
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services import follow_service
from app.services.errors import BadRequestError, ConflictError, NotFoundError


def _dt(y: int, m: int, d: int, h: int = 10) -> datetime:
    return datetime(y, m, d, h, 0, 0, tzinfo=timezone.utc)


async def _make_user(
    db_session: AsyncSession, username: str, email: str | None = None
) -> User:
    """Cria e commita um usuário local ao teste."""
    from uuid6 import uuid7

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


# ===== Service: follow_user =====


@pytest.mark.asyncio
async def test_follow_creates_relation(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo1")

    await follow_service.follow_user(db_session, test_user.id, alvo.id)

    row = (
        await db_session.execute(
            select(Follow).where(
                Follow.follower_id == test_user.id,
                Follow.following_id == alvo.id,
            )
        )
    ).scalar_one_or_none()
    assert row is not None


@pytest.mark.asyncio
async def test_follow_self_raises_bad_request(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(BadRequestError) as exc_info:
        await follow_service.follow_user(db_session, test_user.id, test_user.id)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_follow_nonexistent_user_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await follow_service.follow_user(db_session, test_user.id, uuid4())
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_follow_duplicate_raises_conflict(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo2")
    alvo_id = alvo.id  # captura antes do rollback do branch de conflito

    await follow_service.follow_user(db_session, test_user.id, alvo_id)

    with pytest.raises(ConflictError) as exc_info:
        await follow_service.follow_user(db_session, test_user.id, alvo_id)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_follow_creates_notification(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo3")

    await follow_service.follow_user(db_session, test_user.id, alvo.id)

    notif = (
        await db_session.execute(
            select(Notification).where(
                Notification.recipient_id == alvo.id,
                Notification.actor_id == test_user.id,
                Notification.type == NotificationType.FOLLOW,
            )
        )
    ).scalar_one_or_none()
    assert notif is not None


@pytest.mark.asyncio
async def test_follow_duplicate_does_not_create_notification(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo4")
    # Captura ids ANTES do rollback do branch de conflito:
    # o rollback expira `alvo` e `test_user`; ler .id depois dispara
    # MissingGreenlet (IO fora do greenlet async).
    alvo_id = alvo.id
    test_user_id = test_user.id

    await follow_service.follow_user(db_session, test_user_id, alvo_id)
    with pytest.raises(ConflictError):
        await follow_service.follow_user(db_session, test_user_id, alvo_id)

    notifs = (
        await db_session.execute(
            select(Notification).where(
                Notification.recipient_id == alvo_id,
                Notification.actor_id == test_user_id,
                Notification.type == NotificationType.FOLLOW,
            )
        )
    ).scalars().all()
    assert len(notifs) == 1


# ===== Service: unfollow_user =====


@pytest.mark.asyncio
async def test_unfollow_removes_relation(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo5")
    await follow_service.follow_user(db_session, test_user.id, alvo.id)

    await follow_service.unfollow_user(db_session, test_user.id, alvo.id)

    row = (
        await db_session.execute(
            select(Follow).where(
                Follow.follower_id == test_user.id,
                Follow.following_id == alvo.id,
            )
        )
    ).scalar_one_or_none()
    assert row is None


@pytest.mark.asyncio
async def test_unfollow_not_following_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo6")

    with pytest.raises(NotFoundError) as exc_info:
        await follow_service.unfollow_user(db_session, test_user.id, alvo.id)
    assert exc_info.value.status_code == 404


# ===== Service: is_following / following_ids_subquery =====


@pytest.mark.asyncio
async def test_is_following_true(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo7")
    await follow_service.follow_user(db_session, test_user.id, alvo.id)

    assert await follow_service.is_following(db_session, test_user.id, alvo.id) is True


@pytest.mark.asyncio
async def test_is_following_false(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "alvo8")
    assert await follow_service.is_following(db_session, test_user.id, alvo.id) is False


@pytest.mark.asyncio
async def test_following_ids_subquery_returns_followed_ids(
    db_session: AsyncSession, test_user: User
) -> None:
    a = await _make_user(db_session, "alvo9")
    b = await _make_user(db_session, "alvo10")
    await follow_service.follow_user(db_session, test_user.id, a.id)
    await follow_service.follow_user(db_session, test_user.id, b.id)

    stmt = follow_service.following_ids_subquery(test_user.id)
    ids = set((await db_session.execute(stmt)).scalars().all())
    assert ids == {a.id, b.id}


# ===== Service: get_followers / get_following =====


@pytest.mark.asyncio
async def test_get_followers_returns_followers(
    db_session: AsyncSession, test_user: User
) -> None:
    f1 = await _make_user(db_session, "f1")
    f2 = await _make_user(db_session, "f2")
    await follow_service.follow_user(db_session, f1.id, test_user.id)
    await follow_service.follow_user(db_session, f2.id, test_user.id)

    result = await follow_service.get_followers(db_session, test_user.id, 10, 0)
    usernames = {u.username for u in result}
    assert usernames == {"f1", "f2"}


@pytest.mark.asyncio
async def test_get_followers_ignores_following(
    db_session: AsyncSession, test_user: User
) -> None:
    """Quem o test_user segue NÃO aparece em followers."""
    alvo = await _make_user(db_session, "alvo11")
    await follow_service.follow_user(db_session, test_user.id, alvo.id)

    result = await follow_service.get_followers(db_session, test_user.id, 10, 0)
    assert alvo.id not in {u.id for u in result}


@pytest.mark.asyncio
async def test_get_followers_nonexistent_user_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError):
        await follow_service.get_followers(db_session, uuid4(), 10, 0)


@pytest.mark.asyncio
async def test_get_following_returns_followed(
    db_session: AsyncSession, test_user: User
) -> None:
    a = await _make_user(db_session, "g1")
    b = await _make_user(db_session, "g2")
    await follow_service.follow_user(db_session, test_user.id, a.id)
    await follow_service.follow_user(db_session, test_user.id, b.id)

    result = await follow_service.get_following(db_session, test_user.id, 10, 0)
    assert {u.username for u in result} == {"g1", "g2"}


@pytest.mark.asyncio
async def test_get_following_pagination(
    db_session: AsyncSession, test_user: User
) -> None:
    users = []
    for i in range(3):
        u = await _make_user(db_session, f"pg{i}")
        await follow_service.follow_user(db_session, test_user.id, u.id)
        users.append(u)

    page1 = await follow_service.get_following(db_session, test_user.id, 2, 0)
    page2 = await follow_service.get_following(db_session, test_user.id, 2, 2)

    assert len(page1) == 2
    assert len(page2) == 1
    assert {u.id for u in page1}.isdisjoint({u.id for u in page2})


# ===== Rotas HTTP =====


@pytest.mark.asyncio
async def test_route_follow_and_unfollow(
    client, test_user: User, db_session: AsyncSession
) -> None:
    alvo = await _make_user(db_session, "alvo_route1")

    r1 = await client.post(f"/users/{alvo.id}/follow")
    assert r1.status_code == 204

    r2 = await client.delete(f"/users/{alvo.id}/follow")
    assert r2.status_code == 204


@pytest.mark.asyncio
async def test_route_follow_self_400(
    client, test_user: User
) -> None:
    r = await client.post(f"/users/{test_user.id}/follow")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_route_follow_duplicate_409(
    client, test_user: User, db_session: AsyncSession
) -> None:
    alvo = await _make_user(db_session, "alvo_route2")

    r1 = await client.post(f"/users/{alvo.id}/follow")
    assert r1.status_code == 204

    r2 = await client.post(f"/users/{alvo.id}/follow")
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_route_follow_nonexistent_user_404(
    client, test_user: User
) -> None:
    r = await client.post(f"/users/{uuid4()}/follow")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_unfollow_not_following_404(
    client, test_user: User, db_session: AsyncSession
) -> None:
    alvo = await _make_user(db_session, "alvo_route3")

    r = await client.delete(f"/users/{alvo.id}/follow")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_list_followers(
    client, test_user: User, db_session: AsyncSession
) -> None:
    f1 = await _make_user(db_session, "rf1")
    await follow_service.follow_user(db_session, f1.id, test_user.id)

    r = await client.get(f"/users/{test_user.id}/followers")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert any(u["username"] == "rf1" for u in body)


@pytest.mark.asyncio
async def test_route_list_following(
    client, test_user: User, db_session: AsyncSession
) -> None:
    a = await _make_user(db_session, "rfo1")
    await follow_service.follow_user(db_session, test_user.id, a.id)

    r = await client.get(f"/users/{test_user.id}/following")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert any(u["username"] == "rfo1" for u in body)


@pytest.mark.asyncio
async def test_route_list_followers_nonexistent_user_404(
    client, test_user: User
) -> None:
    r = await client.get(f"/users/{uuid4()}/followers")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_followers_limit_upper_bound_422(
    client, test_user: User
) -> None:
    r = await client.get(f"/users/{test_user.id}/followers?limit=200")
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_route_followers_limit_lower_bound_422(
    client, test_user: User
) -> None:
    r = await client.get(f"/users/{test_user.id}/followers?limit=0")
    assert r.status_code == 422