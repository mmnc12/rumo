from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityPhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    activity_id: UUID
    url: str
    width: int | None
    height: int | None
    created_at: datetime