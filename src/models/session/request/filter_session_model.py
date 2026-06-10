from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional
from src.enums.session_status_enum import SessionStatusEnum

class FilterSessionModel(BaseModel):
    status: Optional[list[SessionStatusEnum]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    user_id: Optional[str] = None
    offset: int = 0
    limit: int = Field(10,le=100)