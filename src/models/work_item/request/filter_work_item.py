from pydantic import BaseModel, Field
from typing import Optional
from src.enums.work_item_type import WorkItemType
from src.enums.task_priority_enum import TaskPriorityEnum

class FilterWorkItemModel(BaseModel):
    handler_id: Optional[list[str]] = None
    search: Optional[str] = None
    offset: int =0
    limit: int = Field(10, le=100)
    status: Optional[list[str]] = None
    owner_id: Optional[list[str]] = None
    assigned_id: Optional[list[str]] = None
    parent: Optional[str] = None
    type: Optional[list[WorkItemType]] = None
    is_in_sprint: Optional[bool] = None
    priority: Optional[list[TaskPriorityEnum]] = None
    type_order: Optional[str] = None
    list_ids: Optional[list[str]] = None
    project: Optional[list[str]] = None
    group: Optional[list[str]] = None
    is_today: Optional[bool] = False
    deadline_start: Optional[int] = None
    deadline_end: Optional[int] = None
    sprint: Optional[list[str]] = None
    task: Optional[str] = None
    session_id: Optional[str] = None

class ParentStatusCount(BaseModel):
    parent: str
    status: str
    count: int
