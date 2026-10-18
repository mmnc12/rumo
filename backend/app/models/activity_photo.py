from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.database import Base

if TYPE_CHECKING:
    from app.models.activity import Activity


class ActivityPhoto(Base):
    __tablename__ = "activity_photos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    activity_id: Mapped[UUID] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    public_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    width: Mapped[int | None] = mapped_column(nullable=True)
    height: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    activity: Mapped["Activity"] = relationship(
        "Activity",
        back_populates="photos",
        lazy="raise",
    )