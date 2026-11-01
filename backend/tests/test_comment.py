"""Testes de comment_service (service + rotas HTTP).

Cobre:
- create_comment (cria notificação, valida atividade existente)
- list_comments (ordenação asc, selectinload do user)
- delete_comment (só autor, 403 para qualquer outro, 404 inexistente)
- Rotas POST/GET /activities/{id}/comments e DELETE /comments/{id}

Padrão: @pytest.mark.asyncio sem scope; helper _make_activity cria
Activity mínimo direto no db_session; helper _make_user idem.

Armadilha: Comment.user é lazy="raise" — só acessar .user em objetos
que passaram por selectinload (retorno de create_comment/list_comments).
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from app.models.activity import Activity, ActivityType
from app.models.comment import Comment
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services import comment_service
from app.services.errors import ForbiddenError, NotFoundError


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


# ===== Service: create_comment =====


@pytest.mark.asyncio
async def test_create_comment_returns_with_user_loaded(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "c_owner1")
    act = await _make_activity(db_session, owner)

    result = await comment_service.create_comment(
        db_session, test_user.id, act.id, "primeiro comentário"
    )

    # selectinload(Comment.user) no service — acessar .user aqui é seguro
    assert result.content == "primeiro comentário"
    assert result.user.username == "testuser"
    assert result.activity_id == act.id


@pytest.mark.asyncio
async def test_create_comment_creates_notification(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "c_owner2")
    act = await _make_activity(db_session, owner)
    owner_id = owner.id
    test_user_id = test_user.id
    act_id = act.id

    result = await comment_service.create_comment(
        db_session, test_user_id, act_id, "olá"
    )
    comment_id = result.id

    notif = (
        await db_session.execute(
            select(Notification).where(
                Notification.recipient_id == owner_id,
                Notification.actor_id == test_user_id,
                Notification.type == NotificationType.COMMENT,
                Notification.activity_id == act_id,
                Notification.comment_id == comment_id,
            )
        )
    ).scalar_one_or_none()
    assert notif is not None


@pytest.mark.asyncio
async def test_create_comment_nonexistent_activity_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await comment_service.create_comment(
            db_session, test_user.id, uuid4(), "x"
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_create_two_comments_creates_two_notifications(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "c_owner3")
    act = await _make_activity(db_session, owner)
    owner_id = owner.id
    test_user_id = test_user.id
    act_id = act.id

    await comment_service.create_comment(db_session, test_user_id, act_id, "a")
    await comment_service.create_comment(db_session, test_user_id, act_id, "b")

    notifs = (
        await db_session.execute(
            select(Notification).where(
                Notification.recipient_id == owner_id,
                Notification.actor_id == test_user_id,
                Notification.type == NotificationType.COMMENT,
            )
        )
    ).scalars().all()
    assert len(notifs) == 2


# ===== Service: list_comments =====


@pytest.mark.asyncio
async def test_list_comments_empty_returns_empty_list(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "c_owner4")
    act = await _make_activity(db_session, owner)

    result = await comment_service.list_comments(db_session, act.id, 10, 0)
    assert result == []


@pytest.mark.asyncio
async def test_list_comments_ordering_asc(
    db_session: AsyncSession, test_user: User
) -> None:
    """Mais antigo primeiro (created_at.asc())."""
    owner = await _make_user(db_session, "c_owner5")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    await comment_service.create_comment(db_session, test_user_id, act_id, "primeiro")
    await comment_service.create_comment(db_session, test_user_id, act_id, "segundo")
    await comment_service.create_comment(db_session, test_user_id, act_id, "terceiro")

    result = await comment_service.list_comments(db_session, act_id, 10, 0)
    contents = [c.content for c in result]
    assert contents == ["primeiro", "segundo", "terceiro"]


@pytest.mark.asyncio
async def test_list_comments_loads_user(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "c_owner6")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    await comment_service.create_comment(db_session, test_user_id, act_id, "x")

    result = await comment_service.list_comments(db_session, act_id, 10, 0)
    assert len(result) == 1
    # selectinload garante .user carregado — acessar não estoura
    assert result[0].user.username == "testuser"


@pytest.mark.asyncio
async def test_list_comments_nonexistent_activity_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await comment_service.list_comments(db_session, uuid4(), 10, 0)
    assert exc_info.value.status_code == 404


# ===== Service: delete_comment =====


@pytest.mark.asyncio
async def test_delete_comment_by_author(
    db_session: AsyncSession, test_user: User
) -> None:
    owner = await _make_user(db_session, "c_owner7")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    created = await comment_service.create_comment(
        db_session, test_user_id, act_id, "vou deletar"
    )
    comment_id = created.id

    await comment_service.delete_comment(db_session, test_user_id, comment_id)

    row = (
        await db_session.execute(
            select(Comment).where(Comment.id == comment_id)
        )
    ).scalar_one_or_none()
    assert row is None


@pytest.mark.asyncio
async def test_delete_comment_by_non_author_forbidden(
    db_session: AsyncSession, test_user: User
) -> None:
    """Quem não é o autor do comentário NÃO pode deletar."""
    author = await _make_user(db_session, "c_author8")
    owner = await _make_user(db_session, "c_owner8")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    author_id = author.id

    created = await comment_service.create_comment(
        db_session, author_id, act_id, "comentário do author"
    )
    comment_id = created.id

    with pytest.raises(ForbiddenError) as exc_info:
        await comment_service.delete_comment(
            db_session, test_user.id, comment_id
        )
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_by_activity_owner_forbidden(
    db_session: AsyncSession, test_user: User
) -> None:
    """Dono da atividade ≠ autor do comentário → 403.

    Regra real do service é mais restritiva que "dono da atividade pode
    moderar": só o AUTOR do comentário deleta.
    """
    comment_author = await _make_user(db_session, "c_author9")
    activity_owner = test_user  # test_user é dono da atividade
    act = await _make_activity(db_session, activity_owner)
    act_id = act.id
    author_id = comment_author.id

    created = await comment_service.create_comment(
        db_session, author_id, act_id, "comentário de outro"
    )
    comment_id = created.id

    # test_user é dono da atividade mas NÃO é autor do comentário
    with pytest.raises(ForbiddenError) as exc_info:
        await comment_service.delete_comment(
            db_session, test_user.id, comment_id
        )
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_nonexistent_raises_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await comment_service.delete_comment(db_session, test_user.id, uuid4())
    assert exc_info.value.status_code == 404


# ===== Rotas HTTP =====


@pytest.mark.asyncio
async def test_route_create_comment_shape(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "c_owner_route1")
    act = await _make_activity(db_session, owner)

    r = await client.post(
        f"/activities/{act.id}/comments",
        json={"content": "comentário via rota"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["content"] == "comentário via rota"
    assert body["activity_id"] == str(act.id)
    assert "id" in body
    assert body["author"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_route_create_comment_empty_content_422(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "c_owner_route2")
    act = await _make_activity(db_session, owner)

    r = await client.post(
        f"/activities/{act.id}/comments",
        json={"content": ""},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_route_create_comment_too_long_422(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "c_owner_route3")
    act = await _make_activity(db_session, owner)

    r = await client.post(
        f"/activities/{act.id}/comments",
        json={"content": "x" * 501},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_route_create_comment_nonexistent_activity_404(
    client, test_user: User
) -> None:
    r = await client.post(
        f"/activities/{uuid4()}/comments",
        json={"content": "x"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_list_comments_shape(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "c_owner_route4")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    await comment_service.create_comment(db_session, test_user_id, act_id, "a")
    await comment_service.create_comment(db_session, test_user_id, act_id, "b")

    r = await client.get(f"/activities/{act_id}/comments")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert [c["content"] for c in body] == ["a", "b"]
    assert body[0]["author"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_route_list_comments_nonexistent_activity_404(
    client, test_user: User
) -> None:
    r = await client.get(f"/activities/{uuid4()}/comments")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_delete_comment_by_author(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "c_owner_route5")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    test_user_id = test_user.id

    created = await comment_service.create_comment(
        db_session, test_user_id, act_id, "vou deletar via rota"
    )
    comment_id = created.id

    r = await client.delete(f"/comments/{comment_id}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_route_delete_comment_by_non_author_403(
    client, test_user: User, db_session: AsyncSession
) -> None:
    author = await _make_user(db_session, "c_author_route6")
    owner = await _make_user(db_session, "c_owner_route6")
    act = await _make_activity(db_session, owner)
    act_id = act.id
    author_id = author.id

    created = await comment_service.create_comment(
        db_session, author_id, act_id, "comentário de outro"
    )
    comment_id = created.id

    r = await client.delete(f"/comments/{comment_id}")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_route_delete_nonexistent_comment_404(
    client, test_user: User
) -> None:
    r = await client.delete(f"/comments/{uuid4()}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_route_list_comments_limit_upper_bound_422(
    client, test_user: User, db_session: AsyncSession
) -> None:
    owner = await _make_user(db_session, "c_owner_route7")
    act = await _make_activity(db_session, owner)

    r = await client.get(f"/activities/{act.id}/comments?limit=200")
    assert r.status_code == 422