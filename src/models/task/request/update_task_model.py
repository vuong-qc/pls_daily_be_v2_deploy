from pydantic import BaseModel, Field, field_validator, ValidationInfo

from src.enums.task_status_enum import TaskStatusEnum
from typing import Optional
from src.enums.task_priority_enum import TaskPriorityEnum

class UpdateUserTaskModel(BaseModel):
    title: Optional[str] = None
    des: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    time_rush: Optional[int] = None
    review_status: Optional[str] = None
    duration: Optional[int] = None
    type: Optional[str] = None
    parent: Optional[str] = None
    assigned_id: Optional[list[str]] = None
    deadline: Optional[int] = None
    point: Optional[int] = None
    files: Optional[list[str]] = None
    handler_id: Optional[list[str]] = None
    session_id: Optional[str] = None
    is_in_sprint: Optional[bool] = None
    order_type: Optional[str] = None
    next_order: Optional[str] = None
    prev_order: Optional[str] = None

    @field_validator("title", "type", mode="before")
    @classmethod
    def not_allow_null(cls, v, info:ValidationInfo):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be null")
        return v

    @field_validator('title', mode='after')
    @classmethod
    def title_not_blank(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("'title' không được để trống")
        return v.strip() if v else v

class UpdateTaskModel(UpdateUserTaskModel):
    deadline: Optional[int] = None
    point: Optional[int] = None
    files: Optional[list[str]] = None
    assigned_id: Optional[list[str]] = None
    handler_id: Optional[list[str]] = None
    session_id: Optional[str] = None

class UpdateStoryModel(UpdateUserTaskModel):
    assigned_id: Optional[list[str]] = None
    handler_id: Optional[list[str]] = None


