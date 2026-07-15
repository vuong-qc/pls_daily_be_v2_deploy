from beanie import DocumentWithSoftDelete, Link
from typing import Optional

from src.models.user.user_document import UserDocument


class DepartmentDocument(DocumentWithSoftDelete):
    name: str
    des: str
    icon: Optional[str] = None
    chatbot_token_id: Optional[str] = None

    class Settings:
        name = 'department'