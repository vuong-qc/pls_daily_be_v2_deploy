from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from src.models.task.response.task_response_model import TaskResponse
from src.models.user.response.user_response_model import UserResponse
from beanie import PydanticObjectId

class SprintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    assignee: Optional[List[UserResponse]] = None
    type: str
    title: str
    des: Optional[str] = None
    status: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    duration: Optional[int] = None
    assigned_id: Optional[list[str]] = None
    parent: Optional[str] = None
    total_tasks: Optional[int] = None
    done_tasks: Optional[int] = None
    order: Optional[str] = None
