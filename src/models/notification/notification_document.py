from typing import List, Optional
from beanie import DocumentWithSoftDelete, before_event, Update
from pydantic import Field

from src.utils.datetime_util import DateTimeUtil


class NotificationDocument(DocumentWithSoftDelete):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    is_active: bool = Field(default=True)
    type: str
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    duration: Optional[int] = None
    files: Optional[List[str]] = None
    owner_id: str
    departments: list[str]
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    viewer_ids: list[str] = []
    class Settings:
        name = "notifications"

    @before_event(Update)
    def update_timestamp_on_update(self):
        self.updated_at = DateTimeUtil.current_milli_time()