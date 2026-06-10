from typing import Optional

from beanie import DocumentWithSoftDelete
from datetime import datetime

class SessionDocument(DocumentWithSoftDelete):
    user_id: str
    status: str
    list_task: list[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str