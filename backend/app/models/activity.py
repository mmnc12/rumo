import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.database import Base


class ActivityType(str, enum.Enum):
    """Tipos de atividade suportados."""
    RUN = "run"
    WALK = "walk"
    CYCLE = "cycle"
    HIKE = "hike"
    SWIM = "swim"
    OTHER = "other"


class Activity(Base):
    """Uma atividade física registrada pelo usuário."""

    __tablename__ = "activities"

    # Chave primária
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )

    # Dono da atividade
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo da atividade
    activity_type: Mapped[ActivityType] = mapped_column(
        SQLEnum(ActivityType, name="activity_type_enum", native_enum=True),
        nullable=False,
    )

    # Metadados descritivos
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_s: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Métricas
    distance_m: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    elevation_gain_m: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_pace_s_per_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_speed_mps: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Rota GPS armazenada como LINESTRING (SRID 4326 = WGS84, o padrão de GPS)
    route: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326),
        nullable=True,
    )

    # Pontos brutos com detalhes (altitude, precisão, etc.)
    raw_track_points: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Controle
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relacionamento com User (opcional, útil para queries futuras)
    user = relationship("User", backref="activities")

    # Constraints de sanidade
    __table_args__ = (
        CheckConstraint("distance_m IS NULL OR distance_m >= 0", name="ck_distance_non_negative"),
        CheckConstraint("duration_s IS NULL OR duration_s >= 0", name="ck_duration_non_negative"),
        CheckConstraint("calories IS NULL OR calories >= 0", name="ck_calories_non_negative"),
        Index("ix_activities_user_started", "user_id", "started_at"),
    )

    def __repr__(self) -> str:
        return f"<Activity {self.activity_type.value} by user={self.user_id}>"