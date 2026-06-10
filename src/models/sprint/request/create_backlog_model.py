from pydantic import BaseModel, field_validator, Field
from typing import  Optional
from src.enums.sprint_status_enum import SprintStatusEnum
from src.enums.work_item_type import WorkItemType
from src.utils.datetime_util import DateTimeUtil

class CreateBacklogModel(BaseModel):
    title: str
    des: Optional[str] = None
    status: SprintStatusEnum = SprintStatusEnum.NEW
    parent: str
    type: WorkItemType = WorkItemType.BACKLOG
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
