from beanie import DocumentWithSoftDelete, Link, before_event, Update
from pydantic import Field

from src.models.user.user_document import UserDocument
from src.utils.datetime_util import DateTimeUtil
from typing import Optional

class EvaluateDocument(DocumentWithSoftDelete):
    creator_id: str
    assigned_id: str
    update_user: Optional[str] = None
    title: str
    description: Optional[str]= None
    value: Optional[int] = None
    point: Optional[int] = None
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    creator_model: Optional[Link[UserDocument]] = None
    assigned_model: Optional[Link[UserDocument]] = None
    updated_model: Optional[Link[UserDocument]] = None

    class Settings:
        name= "evaluates"

    @before_event(Update)
    def updated_at_millisecond(self):
        self.updated_at = DateTimeUtil.current_milli_time()