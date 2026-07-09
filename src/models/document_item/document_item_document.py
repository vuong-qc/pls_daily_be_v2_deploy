from typing import Optional

from beanie import DocumentWithSoftDelete

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

    class Settings:
        name='document_items'