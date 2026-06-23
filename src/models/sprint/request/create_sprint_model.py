from pydantic import BaseModel, field_validator, Field
from typing import  Optional
from src.enums.sprint_status_enum import SprintStatusEnum
from src.enums.work_item_type import WorkItemType
from src.utils.datetime_util import DateTimeUtil

class CreateSprintModel(BaseModel):
    duration: Optional[int] = None
    start: Optional[int] = None
    end: Optional[int] = None
    title: str
    des: Optional[str] = None
    status: SprintStatusEnum = SprintStatusEnum.NEW
    parent: str
    assigned_id: Optional[list[str]] = None
    type: WorkItemType = WorkItemType.SPRINT
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    order_type: Optional[str] = None
    next_order: Optional[str] = None
    prev_order: Optional[str] = None


    @field_validator("type",mode="before")
    @classmethod
    def type_validator(cls, v):
        return WorkItemType.SPRINT