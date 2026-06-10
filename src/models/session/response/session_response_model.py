from typing import Optional

from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from datetime import datetime

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    user_id: str
    status: str
    list_task: list[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str