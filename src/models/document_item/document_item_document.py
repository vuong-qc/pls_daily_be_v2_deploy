from typing import Optional

from src.models.work_item.work_item_document import WorkItemDocument
from src.models.user.user_document import UserDocument
from beanie import DocumentWithSoftDelete, Link, before_event, Update
from src.utils.datetime_util import DateTimeUtil
from pydantic import Field

class DocumentItem(DocumentWithSoftDelete):
    group_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    type: str
    date_time: int
    object_id: Optional[str] = None
    parent_type: Optional[str] = None
    created_by: Optional[str] = None
    is_archived: Optional[bool] = False
    is_checked: Optional[bool] = False
    is_urgent: Optional[bool] = False
    priority: Optional[str] = None
    notes: Optional[str] = None
    assignee: Optional[list[str]] = None
    sprint: Optional[str] = None
    task: Optional[str] = None
    precondition: Optional[str] = None
    step_implement: Optional[str] = None
    role: Optional[str] = None
    data_test: Optional[str] = None
    expect_result: Optional[str] = None
    final_result: Optional[str] = None
    handler: Optional[str] = None
    scenario: Optional[str] = None
    feature: Optional[str] = None
    assignee_model: Optional[list[Link[UserDocument]]] = None
    handler_model: Optional[Link[UserDocument]] = None
    task_model: Optional[Link[WorkItemDocument]] = None
    sprint_model: Optional[Link[WorkItemDocument]] = None
    deadline: Optional[int] = None
    duration: Optional[int] = None
    details: Optional[str] = None
    ftf: Optional[bool] = None
    is_closed: Optional[bool] = False
    updated_at: Optional[int] = Field(default_factory=DateTimeUtil.current_milli_time)
    created_by_model: Optional[Link[UserDocument]] = None
    parent_id: Optional[str] = None

    class Settings:
        name='document_items'

    @before_event(Update)
    def updated_at_millisecond(self):
        self.updated_at = DateTimeUtil.current_milli_time()