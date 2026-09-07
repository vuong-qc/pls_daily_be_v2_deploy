from typing import Optional
from beanie import DocumentWithSoftDelete, Link, Update, before_event
from pydantic import Field
from src.models.user.user_document import UserDocument
from src.utils.datetime_util import DateTimeUtil

class VersionDocument(DocumentWithSoftDelete):
    creator_id: str
    type: str
    object_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    creator_model: Optional[Link[UserDocument]] = None
    updator_model: Optional[Link[UserDocument]] = None
    updator_id: Optional[str] = None
    version: Optional[str] = None

    class Settings:
        name = "versions"

    @before_event(Update)
    def update_time(self):
        self.updated_at = DateTimeUtil.current_milli_time()
