"""Service de usuários: busca por username/full_name."""

from uuid import UUID

from sqlalchemy import case, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.errors import ServiceError


async def search_users(
    db: AsyncSession,
    q: str,
    current_user_id: UUID,
    limit: int = 20,
) -> list[User]:
    """Busca usuários por username ou full_name (ILIKE, case-insensitive).

    Regras:
    - Termo mínimo de 2 caracteres (evita full scan de 1 char).
    - Exclui o próprio usuário dos resultados (não faz sentido seguir a si mesmo).
    - Exclui usuários inativos.
    - Ordena por relevância: prefixo em username > prefixo em full_name > contém.

    Sem índice pg_trgm por enquanto (volume atual é baixo; full scan é trivial).
    Quando o app passar de ~5k usuários, criar índice GIN com gin_trgm_ops.
    """
    term = q.strip()
    if len(term) < 2:
        raise ServiceError(400, "Termo de busca deve ter ao menos 2 caracteres")

    pattern = f"%{term}%"
    prefix = f"{term}%"

    # Ranking de relevância (0 = melhor). Desempate por username ASC.
    relevance = case(
        (User.username.ilike(prefix), 0),
        (User.full_name.ilike(prefix), 1),
        else_=2,
    )

    stmt = (
        select(User)
        .where(
            User.is_active.is_(True),
            User.id != current_user_id,
            or_(
                User.username.ilike(pattern),
                User.full_name.ilike(pattern),
            ),
        )
        .order_by(relevance, User.username.asc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())