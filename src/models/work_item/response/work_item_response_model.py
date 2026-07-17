from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Any
from src.models.user.response.user_response_model import UserResponse
from beanie import PydanticObjectId, BackLink, Link
from src.models.group.response.group_reponse_model import GroupResponse
class WorkItemResponse(BaseModel):
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
    children: Optional[list['WorkItemResponse']] = None
    time_rush: Optional[int] = None
    review_status: Optional[str] = None
    is_in_sprint: Optional[bool] = None
    updated_at: int
    created_at: int
    duration: Optional[int] = None
    parent_model: Optional['WorkItemResponse'] = None

    owner_id: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    note: Optional[str] = None
    comment: Optional[str] = None
    link: Optional[str] = None
    owner: Optional[UserResponse] = None
    session_id: Optional[str] = None

    project: Optional[str] = None
    group: Optional[str] = None
    sprint: Optional[str] = None
    task: Optional[str] = None

    project_model: Optional['WorkItemResponse'] = None
    group_model: Optional['GroupResponse'] = None
    sprint_model: Optional['WorkItemResponse'] = None
    task_model: Optional['WorkItemResponse'] = None
    explanation: Optional[str] = None

    screen: Optional[str] = None
    action: Optional[str] = None
    blame: Optional[str] = None
    extra_info: Optional[str] = None
    platform: Optional[str] = None
    device: Optional[str] = None
    device_version: Optional[str] = None
    project_version: Optional[str] = None
    bug_type: Optional[str] = None

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
    @field_validator(
        "owner", mode='before'
    )
    @classmethod
    def handle_owner(cls, v):
        if isinstance(v, Link):
            return None

        if isinstance(v, list) and all(isinstance(item, Link) for item in v):
            return None
        return v


WorkItemResponse.model_rebuild()