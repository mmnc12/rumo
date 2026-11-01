"""Testes de like_service (service + rotas HTTP).

Cobre:
- like_activity (idempotente, notificação só no primeiro like)
- unlike_activity (idempotente, silencioso se não existe)
- get_likes (contagem, flag liked_by_me, lista de usuários)
- Rotas POST/DELETE /activities/{id}/like e GET /activities/{id}/likes

Padrão: @pytest.mark.asyncio sem scope; helper _make_activity cria
Activity mínimo direto no db_session (evita acoplar ao activity_service).

Armadilha do MissingGreenlet: like_activity faz rollback() no branch
idempotente. Isso expira TODOS os ORM attached à sessão. Capturar .id
em variável ANTES de qualquer chamada que possa disparar rollback.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from app.models.activity import Activity, ActivityType
from app.models.like import Like
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services import like_service
from app.services.errors import NotFoundError


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
) -> Activity:
    """Cria Activity mínimo (campos NOT NULL sem default).

    Não usa activity_service.create_activity — evita acoplar o teste de
    like ao serviço de atividade. Só seta o que o banco exige.
    """
    activity = Activity(
        id=uuid7(),
        user_id=owner.id,
        activity_type=activity_type,
        started_at=started_at or _dt(2026, 1, 5),
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity


# ===== Service: like_activity =====


@pytest.mark.asyncio
async def test_like_creates_like_and_returns_state(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "owner_like1")
    act = await _make_activity(db_session, alvo)
    act_id = act.id

    state = await like_service.like_activity(db_session, test_user.id, act_id)

    assert state == {"count": 1, "liked_by_me": True}

    row = (
        await db_session.execute(
            select(Like).where(
                Like.user_id == test_user.id,
                Like.activity_id == act_id,
            )
        )
    ).scalar_one_or_none()
    assert row is not None


@pytest.mark.asyncio
async def test_like_creates_notification(
    db_session: AsyncSession, test_user: User
) -> None:
    alvo = await _make_user(db_session, "owner_like2")
    act = await _make_activity(db_session, alvo)
    act_id = act.id
    alvo_id = alvo.id
    test_user_id = test_user.id

    await like_service.like_activity(db_session, test_user_id, act_id)

    notif = (
        await db_session.execute(
            select(Notification).where(
                Notification.recipient_id == alvo_id,
                Notification.actor_id == test_user_id,
                Notification.type == NotificationType.LIKE,
                Notification.activity_id == act_id,
            )
        )
    ).scalar_one_or_none()
    assert notif is not None


@pytest.mark.asyncio
async def test_like_idempotent_does_not_create_duplicate(
    db_session: AsyncSession, test_user: User
) -> None:
    """Segundo like no mesmo par (user, activity) é idempotente.

    Captura ids ANTES: o branch idempotente faz rollback() e expira
    todos os ORM attached — ler .id depois estoura MissingGreenlet.
    """
    alvo = await _make_user(db_session, "owner_like3")
    act = await _make_activity(db_session, alvo)
    act_id = act.id
    alvo_id = alvo.id
    test_user_id = test_user.id

    first = await like_service.like_activity(db_session, test_user_id, act_id)
    second = await like_service.like_activity(db_session, test_user_id, act_id)

    assert first == {"count": 1, "liked_by_me": True}
    assert second == {"count": 1, "liked_by_me": True}

    rows = (
        await db_session.execute(
            select(Like).where(
                Like.user_id == test_user_id,
                Like.activity_id == act_id,
            )
        )
    ).scalars().all()
    assert len(rows) == 1

    notifs = (
        await db_session.execute(
            select(Notification).where(
                Notification.recipient_id == alvo_id,
                Notification.actor_id == test_user_id,
                Notification.type == NotificationType.LIKE,
            )
        )
    ).scalars().all()
    assert len(notifs) == 1


@pytest.mark.asyncio
async def test_like_nonexistent_activity_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await like_service.like_activity(db_session, test_user.id, uuid4())
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_like_multiple_users_count(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "owner_like4")
    other = await _make_user(db_session, "liker_like4")
    act = await _make_activity(db_session, owner)
    act_id = act.id

    await like_service.like_activity(db_session, test_user.id, act_id)
    state = await like_service.like_activity(db_session, other.id, act_id)

    assert state == {"count": 2, "liked_by_me": True}


# ===== Service: unlike_activity =====


@pytest.mark.asyncio
async def test_unlike_removes_like(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "owner_unlike1")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    await like_service.like_activity(db_session, test_user_id, act_id)
    await like_service.unlike_activity(db_session, test_user_id, act_id)

    row = (
        await db_session.execute(
            select(Like).where(
                Like.user_id == test_user_id,
                Like.activity_id == act_id,
            )
        )
    ).scalar_one_or_none()
    assert row is None


@pytest.mark.asyncio
async def test_unlike_idempotent_silent(
    db_session: AsyncSession, test_user: User
) -> None:
    """Unlike sem like prévio NÃO levanta erro (assimetria intencional
    em relação a unfollow_user, que levanta 404)."""
    owner = await _make_user(db_session, "owner_unlike2")
    act = await _make_activity(db_session, owner)

    # Não deve levantar
    await like_service.unlike_activity(db_session, test_user.id, act.id)


@pytest.mark.asyncio
async def test_unlike_nonexistent_activity_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await like_service.unlike_activity(db_session, test_user.id, uuid4())
    assert exc_info.value.status_code == 404


# ===== Service: get_likes =====


@pytest.mark.asyncio
async def test_get_likes_empty(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "owner_get1")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    result = await like_service.get_likes(
        db_session, test_user_id, act_id, 10, 0
    )

    assert result["count"] == 0
    assert result["liked_by_me"] is False
    assert result["users"] == []


@pytest.mark.asyncio
async def test_get_likes_lists_users_and_flag(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "owner_get2")
    u2 = await _make_user(db_session, "liker_get2")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    await like_service.like_activity(db_session, test_user_id, act_id)
    await like_service.like_activity(db_session, u2.id, act_id)

    result = await like_service.get_likes(
        db_session, test_user_id, act_id, 10, 0
    )

    assert result["count"] == 2
    assert result["liked_by_me"] is True
    usernames = {u.username for u in result["users"]}
    assert usernames == {"testuser", "liker_get2"}


@pytest.mark.asyncio
async def test_get_likes_liked_by_me_false_for_non_liker(
    db_session: AsyncSession, test_user: User
) -> None:
    """test_user não curtiu; outro curtiu. liked_by_me=False."""
    owner = await _make_user(db_session, "owner_get3")
    u2 = await _make_user(db_session, "liker_get3")
    act = await _make_activity(db_session, owner)
    act_id = act.id

    await like_service.like_activity(db_session, u2.id, act_id)

    result = await like_service.get_likes(
        db_session, test_user.id, act_id, 10, 0
    )

    assert result["count"] == 1
    assert result["liked_by_me"] is False
    assert {u.username for u in result["users"]} == {"liker_get3"}


@pytest.mark.asyncio
async def test_get_likes_nonexistent_activity_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await like_service.get_likes(db_session, test_user.id, uuid4(), 10, 0)
    assert exc_info.value.status_code == 404


# ===== Rotas HTTP =====


@pytest.mark.asyncio
async def test_route_like_and_unlike(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "owner_route1")
    act = await _make_activity(db_session, owner)

    r1 = await client.post(f"/activities/{act.id}/like")
    assert r1.status_code == 200
    body = r1.json()
    assert body == {"count": 1, "liked_by_me": True}

    r2 = await client.delete(f"/activities/{act.id}/like")
    assert r2.status_code == 204


@pytest.mark.asyncio
async def test_route_like_idempotent_returns_current_state(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "owner_route2")
    act = await _make_activity(db_session, owner)

    r1 = await client.post(f"/activities/{act.id}/like")
    r2 = await client.post(f"/activities/{act.id}/like")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json() == {"count": 1, "liked_by_me": True}


@pytest.mark.asyncio
async def test_route_like_nonexistent_activity_404(
    client, test_user: User
) -> None:
    r = await client.post(f"/activities/{uuid4()}/like")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_unlike_nonexistent_activity_404(
    client, test_user: User
) -> None:
    r = await client.delete(f"/activities/{uuid4()}/like")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_get_likes_shape(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "owner_route3")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    await like_service.like_activity(db_session, test_user_id, act_id)

    r = await client.get(f"/activities/{act_id}/likes")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 1
    assert body["liked_by_me"] is True
    assert len(body["users"]) == 1
    assert body["users"][0]["username"] == "testuser"


@pytest.mark.asyncio
async def test_route_get_likes_nonexistent_activity_404(
    client, test_user: User
) -> None:
    r = await client.get(f"/activities/{uuid4()}/likes")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_get_likes_limit_upper_bound_422(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "owner_route4")
    act = await _make_activity(db_session, owner)

    r = await client.get(f"/activities/{act.id}/likes?limit=200")
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_route_get_likes_offset_negative_422(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "owner_route5")
    act = await _make_activity(db_session, owner)

    r = await client.get(f"/activities/{act.id}/likes?offset=-1")
    assert r.status_code == 422