from typing import Optional

from beanie import DocumentWithSoftDelete, Link
from datetime import datetime

from src.models.user.user_document import UserDocument
class SessionDocument(DocumentWithSoftDelete):
    user_id: str
    status: str
    list_task: list[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str
    user: Optional[Link[UserDocument]] = None
