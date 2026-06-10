from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from src.utils.datetime_util import DateTimeUtil
from src.enums.work_item_type import WorkItemType
from src.enums.project_status_enum import ProjectStatusEnum

class CreateProjectModel(BaseModel):
    title: str
    parent: str
    des: Optional[str] = None
    handler_id: Optional[List[str]] = None
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    type: WorkItemType = WorkItemType.PROJECT
    status: ProjectStatusEnum = ProjectStatusEnum.ACTIVE
    owner_id: Optional[str] = None

    @field_validator("type", mode="before")
    @classmethod
    def status_validator(cls, v):
        return WorkItemType.PROJECT
