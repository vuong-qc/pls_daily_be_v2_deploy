from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from src.models.user.response.user_response_model import UserResponse
from beanie import PydanticObjectId

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    type: str
    title: str
    des: Optional[str] = None
    status: str
    parent: str
    deadline: Optional[int] = None
    point: Optional[int] = None
    files: Optional[list[str]] = None
    assigned_id: Optional[list[str]] = None
    handler_id: Optional[list[str]] = None
    priority: Optional[str] = None
    handler: Optional[list[UserResponse]] = None
    assignee: Optional[list[UserResponse]] = None
    children: Optional[list['TaskResponse']] = None
    time_rush: Optional[int] = None
    review_status: Optional[str] = None
    is_in_sprint: Optional[bool] = None
    updated_at: int
    created_at: int
    duration: Optional[int] = None
    parent_model: Optional['TaskResponse'] = None

TaskResponse.model_rebuild()