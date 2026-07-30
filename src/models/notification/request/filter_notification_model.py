from pydantic import BaseModel, Field
from typing import Optional

class FilterNotificationModel(BaseModel):
    is_active: Optional[bool] = None

    limit: int = Field(10, le=100)
    offset: int = Field(default=0)

    type: Optional[str] = None
    is_random: Optional[bool] = False
    is_expired: Optional[bool] = None
    search: Optional[str] = None
    departments: Optional[list[str]] = None
    viewer_ids: Optional[list[str]] = None
    expired_or_active: Optional[bool] = None