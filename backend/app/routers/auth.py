from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
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
    await db.refresh(user)

    return user


@router.post(
    "/login",
    summary="Login (form-urlencoded, padrão OAuth2)",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Autentica o usuário e retorna um access token JWT.

    - Aceita `username` (na verdade, o email) e `password` via form-urlencoded
    - Retorna `{access_token, token_type}`
    - Use o token no header: `Authorization: Bearer <token>`
    """
    # 1. Busca o usuário pelo email (o campo `username` do form é o email)
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    # 2. Verifica se o usuário existe e a senha confere
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verifica se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    # 4. Gera o token
    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Retorna os dados do usuário autenticado",
)
async def me(current_user: User = Depends(get_current_user)):
    """
    Endpoint protegido que retorna os dados do usuário logado.

    Requer header: `Authorization: Bearer <token>`
    """
    return current_user