from typing import Optional

from beanie import Document

class LogDocument(Document):
    user: str
    text: str
    type: str
    position: Optional[str] = None
    object_id: str
    created_at: int
    action: Optional[str] = None
    duration: Optional[int] = None

    class Settings:
        name = "logs"