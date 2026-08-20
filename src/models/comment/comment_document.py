from typing import Optional

import pymongo
from pymongo import IndexModel

from src.utils.datetime_util import DateTimeUtil
from beanie import DocumentWithSoftDelete, Update, before_event, Link
from pydantic import Field
from src.models.user.user_document import UserDocument

class CommentDocument(DocumentWithSoftDelete):
    object_id: str
    creator_id: str
    parent_id: Optional[str] = None
    content: str
    ancestors: list[str] = []
    reply_count: int = 0
    mentions: list[str] = []
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    creator: Link[UserDocument]

    class Settings:
        name = "comments"
        indexes = [
            "object_id",
            "creator_id",
            "parent_id",
            IndexModel([("parent_id", pymongo.DESCENDING), ("created_at", pymongo.DESCENDING)]),
            IndexModel([("object_id", pymongo.DESCENDING), ("created_at", pymongo.DESCENDING)]),
        ]

    @before_event(Update)
    def before_update(self):
        self.updated_at = DateTimeUtil.current_milli_time()