from typing import Optional
from src.utils.datetime_util import DateTimeUtil
from beanie import DocumentWithSoftDelete, before_event, Update
from pydantic import Field

class DocumentResult(DocumentWithSoftDelete):
    owner_id: Optional[str] = None
    parent_id: str
    evaluate: Optional[str] = None
    check: Optional[bool] = None
    evaluate_todo: Optional[str] = None
    is_closed: Optional[bool] = False
    created_at: Optional[int] = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: Optional[int] = Field(default_factory=DateTimeUtil.current_milli_time)

    class Settings:
        name='document_result'
        indexes = {
            'owner_id',
            'parent_id'
        }

    @before_event(Update)
    def update_timestamp_on_update(self):
        self.updated_at = DateTimeUtil.current_milli_time()