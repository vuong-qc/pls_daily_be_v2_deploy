from pydantic import BaseModel, Field
from src.utils.datetime_util import DateTimeUtil
from typing import List, Optional

class CreateNotificationModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    is_active: bool = Field(default=True)
    type: str
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    duration: Optional[int] = None
    files: Optional[List[str]] = None
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    owner_id: Optional[str] = None
    departments: list[str]
    is_celebration: Optional[bool] = None
