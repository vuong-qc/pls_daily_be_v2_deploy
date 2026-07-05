from pydantic import BaseModel
from typing import Optional

class ProjectUsername(BaseModel):
    name: str
    roles: list[int]
    daily_checkin: bool = True
    department: Optional[str] = None
