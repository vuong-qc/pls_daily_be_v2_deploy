from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.models.task.response.task_response_model import TaskResponse
from src.models.document_item.response.document_item_response_model import DocumentResponse
from src.models.user.response.user_response_model import UserResponse
from beanie import PydanticObjectId

class PlanResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    user_id: str
    to_do: Optional[list[str]] = None
    note: Optional[str] = None
    task: Optional[list[str]] = None
    date: int
    user_model: Optional[UserResponse] = None
    task_model: Optional[list[TaskResponse]] = None
    todo_model: Optional[list[DocumentResponse]] = None
