from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from beanie import PydanticObjectId

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    is_active: bool = Field(default=True)
    type: str
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    duration: Optional[int] = None
    files: Optional[List[str]] = None
    viewer_ids: Optional[List[str]] = None
    owner_id: str
    departments: list[str]
    created_at: int
    updated_at: int
    is_celebration: Optional[bool] = None