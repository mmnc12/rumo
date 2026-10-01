import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ===== Schemas de entrada (request) =====

class UserCreate(BaseModel):
    """Dados para criar um novo usuário (cadastro)."""

    email: EmailStr = Field(..., description="Email único do usuário")
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username único (letras, números e _)",
    )
    full_name: str = Field(..., min_length=2, max_length=120)
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Senha em texto puro (será hasheada antes de salvar)",
    )
    weight_kg: float | None = Field(None, gt=0, lt=500, description="Peso em kg")
    height_cm: float | None = Field(None, gt=0, lt=300, description="Altura em cm")
    birth_date: date | None = None


class UserLogin(BaseModel):
    """Credenciais de login (para o futuro endpoint /auth/login)."""

    email: EmailStr
    password: str


# ===== Schemas de saída (response) =====

class UserResponse(BaseModel):
    """Dados públicos do usuário (o que a API devolve)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str
    weight_kg: float | None
    height_cm: float | None
    birth_date: date | None
    is_active: bool
    created_at: datetime

class UserPublic(BaseModel):
    """Dados públicos de outro usuário (sem email/data de nascimento)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    full_name: str
    is_active: bool