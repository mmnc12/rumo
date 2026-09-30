from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Cria um novo usuário.

    - Valida email/username únicos
    - Hasheia a senha antes de salvar (bcrypt)
    - Retorna os dados públicos do usuário criado (sem senha)
    """

    # 1. Verificar se o email já existe
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    # 2. Verificar se o username já existe
    result = await db.execute(
        select(User).where(User.username == payload.username)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username já cadastrado",
        )

    # 3. Criar o usuário (com senha hasheada)
    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        birth_date=payload.birth_date,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)  # recarrega o objeto com os defaults do banco (created_at, etc.)

    return user