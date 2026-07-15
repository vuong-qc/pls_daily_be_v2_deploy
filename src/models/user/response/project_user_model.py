from pydantic import BaseModel
from typing import Optional

class ProjectUsername(BaseModel):
    name: str
    roles: list[int]
    daily_checkin: Optional[bool] = None
    department: Optional[list[str]] = None
    nickname: Optional[str] = None