from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Any, List
from src.models.user.response.user_response_model import UserResponse
from beanie import PydanticObjectId, Link


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    type: str
    title: str
    des: Optional[str] = None
    status: str
    parent: Optional[str] = None
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
    order: Optional[str] = None
    percent_process: Optional[float] = None

    @field_validator(
        'parent_model', mode='before'
    )
    @classmethod
    def handle_link(cls, v):
        if isinstance(v, Link):
            return None

        return v

    @field_validator(
        'handler', mode='before'
    )
    @classmethod
    def handle_handler(cls, v):
        if isinstance(v, list) and all(isinstance(item, Link) for item in v):
            return None
        return v

    @field_validator(
        'assignee', mode='before'
    )
    @classmethod
    def handle_assignee(cls, v):
        if isinstance(v, Link):
            return None

        if isinstance(v, list) and all(isinstance(item, Link) for item in v):
            return None
        return v

TaskResponse.model_rebuild()