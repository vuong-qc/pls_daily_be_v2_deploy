from pydantic import BaseModel, Field
from src.enums.task_status_enum import TaskStatusEnum
from typing import Optional
from src.utils.datetime_util import DateTimeUtil
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
    is_in_sprint: Optional[bool]

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


