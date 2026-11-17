"""Service de usuários: busca por username/full_name e update do próprio perfil."""

from uuid import UUID

from sqlalchemy import case, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate
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


# [Sessão 39] Update parcial do próprio perfil (PUT /users/me).
# Semântica de "não mandou" vs "mandou null" via model_dump(exclude_unset=True):
#   - campo ausente   -> não toca no banco (exclude_unset filtra)
#   - campo = null    -> limpa o campo (valor None é aplicado)
#   - campo com valor -> atualiza
#
# [Sessão 39 — fix] Recarrega o User na sessão do request via db.get ANTES
# de mutar. Motivo: em produção o get_current_user já devolve o user na
# sessão do request (get_db), então db.get é identity-map hit (sem query).
# Em teste, o override de get_current_user devolve o user da fixture
# (sessão diferente) — sem o db.get, o commit da sessão do request estoura
# InvalidRequestError ("already attached to session X"). O db.get reattach
# o objeto na sessão certa e o commit funciona nos dois cenários.
async def update_me(
    db: AsyncSession,
    user: User,
    payload: UserUpdate,
) -> User:
    """Aplica os campos enviados em UserUpdate ao usuário autenticado.

    Retorna o User recarregado do banco (refresh garante que os valores
    refletem o estado pós-commit, incluindo updated_at).
    """
    data = payload.model_dump(exclude_unset=True)

    if not data:
        # Nada a fazer — idempotente. Devolve o user como está.
        # Sem commit/refresh desnecessário.
        return user

    # Reattach na sessão do request (ver comentário [Sessão 39 — fix]).
    user = await db.get(User, user.id)
    if user is None:
        # Não deveria acontecer: get_current_user já validou que existe.
        # Defensivo — se acontecer, é corrida com delete concorrente.
        raise ServiceError(404, "Usuário não encontrado")

    for field, value in data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user