from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class CreateSessionModel(BaseModel):
    user_id: Optional[str] = None
    status: str
    list_task: list[str]
    start_time: datetime
    notes: str