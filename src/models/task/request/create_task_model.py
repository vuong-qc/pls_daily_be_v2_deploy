from pydantic import BaseModel, field_validator, Field
from src.enums.task_status_enum import TaskStatusEnum
from typing import Optional
from src.enums.work_item_type import WorkItemType
from src.utils.datetime_util import DateTimeUtil
from src.enums.task_priority_enum import TaskPriorityEnum

class CreateUserTaskModel(BaseModel):
    type: WorkItemType = WorkItemType.TASK
    title: str
    des: Optional[str] = None
    status: TaskStatusEnum = TaskStatusEnum.NEW
    parent: str
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    files: Optional[list[str]] = None
    priority: TaskPriorityEnum = TaskPriorityEnum.LOW
    assigned_id: Optional[list[str]] = None
    time_rush: Optional[int] = None
    review_status: Optional[str] = None
    is_in_sprint: bool = True
    duration: Optional[int] = None
    order_type: Optional[str] = None
    next_order: Optional[str] = None
    prev_order: Optional[str] = None

    @field_validator("type", mode="before")
    @classmethod
    def status_validator(cls, v):
        return WorkItemType.TASK

    @field_validator("status", mode="after")
    @classmethod
    def type_validator(cls, v):
        return TaskStatusEnum.NEW

class CreateTaskModel(CreateUserTaskModel):
    deadline: Optional[int]
    point: Optional[int]
    handler_id: Optional[list[str]] = None

class CreateStoryModel(CreateUserTaskModel):
    handler_id: Optional[list[str]] = None
    type: WorkItemType = WorkItemType.STORY

    @field_validator("type", mode="before")
    @classmethod
    def status_validator(cls, v):
        return WorkItemType.STORY

