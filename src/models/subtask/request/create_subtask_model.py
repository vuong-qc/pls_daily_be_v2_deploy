from pydantic import BaseModel, field_validator, Field
from src.enums.task_status_enum import TaskStatusEnum
from typing import Optional
from src.enums.work_item_type import WorkItemType
from src.utils.datetime_util import DateTimeUtil

class CreateSubtaskModel(BaseModel):
    type: WorkItemType = WorkItemType.SUBTASK
    title: str
    status: TaskStatusEnum = TaskStatusEnum.NEW
    parent: str
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    duration: Optional[int] = None
    time_rush: Optional[int] = None
    review_status: Optional[str] = None

    @field_validator("type", mode="before")
    @classmethod
    def status_validator(cls, v):
        return WorkItemType.SUBTASK

    @field_validator("status", mode="after")
    @classmethod
    def type_validator(cls, v):
        return TaskStatusEnum.NEW

