from typing import Optional
from src.models.user.user_document import UserDocument
from src.models.work_item.work_item_document import WorkItemDocument
from src.models.document_item.document_item_document import DocumentItem
from beanie import DocumentWithSoftDelete, Link

class PlanDocument(DocumentWithSoftDelete):
    user_id: str
    to_do: Optional[list[str]] = None
    note: Optional[str] = None
    task: Optional[list[str]] = None
    date: int
    user_model: Optional[Link[UserDocument]] = None
    task_model: Optional[list[Link[WorkItemDocument]]] = None
    todo_model: Optional[list[Link[DocumentItem]]] = None
    class Settings:
        name = "plan"