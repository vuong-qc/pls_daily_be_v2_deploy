from pydantic import BaseModel
from typing import List, Optional

class UpdateNotificationModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    duration: Optional[int] = None
    files: Optional[List[str]] = None
    departments: Optional[list[str]] = None
    is_celebration: Optional[bool] = None
