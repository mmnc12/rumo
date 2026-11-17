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
    # full_name é opcional — o frontend manda null quando o campo vem vazio.
    # max_length=120 alinha com o model. Sem min_length porque null é válido.
    full_name: str | None = Field(default=None, max_length=120)
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Senha em texto puro (será hasheada antes de salvar)",
    )
    weight_kg: float | None = Field(None, gt=0, lt=500, description="Peso em kg")
    height_cm: float | None = Field(None, gt=0, lt=300, description="Altura em cm")
    birth_date: date | None = None


# [Sessão 39] Update parcial do próprio perfil (PUT /users/me).
# Todos os campos são opcionais. A semântica de "não mandou" vs "mandou null"
# é resolvida no service via model_dump(exclude_unset=True):
#   - campo ausente  -> não toca no banco
#   - campo = null   -> limpa o campo (weight_kg/height_cm/full_name)
#   - campo com valor -> atualiza
# extra="forbid" rejeita email/username/senha/hashed_password por essa rota:
#   email e username são chave única e exigem validação de conflito (fora do
#   escopo da S39); senha tem fluxo próprio. Falhar explícito é melhor que
#   aceitar e ignorar.
# As restrições de weight_kg/height_cm/full_name espelham o UserCreate —
# paridade de validação entre cadastro e edição.
class UserUpdate(BaseModel):
    """Atualização parcial do perfil do próprio usuário."""

    model_config = ConfigDict(extra="forbid")

    weight_kg: float | None = Field(None, gt=0, lt=500, description="Peso em kg")
    height_cm: float | None = Field(None, gt=0, lt=300, description="Altura em cm")
    full_name: str | None = Field(default=None, max_length=120)


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
    full_name: str | None
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
    full_name: str | None
    is_active: bool