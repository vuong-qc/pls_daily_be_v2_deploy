from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from src.enums.session_status_enum import SessionStatusEnum


class CreateSessionModel(BaseModel):
    user_id: Optional[str] = None
    status: str = SessionStatusEnum.NEW
    list_task: list[str]
    start_time: datetime
    notes: str