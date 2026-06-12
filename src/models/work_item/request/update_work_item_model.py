from typing import Optional

from pydantic import BaseModel

class UpdateWorkItemModel(BaseModel):
    updated_at: Optional[int]
    parent: Optional[str]
    assigned_id: Optional[list[str]]
    start: Optional[int]
    end: Optional[int]
    duration: Optional[int]
    handler_id: Optional[list[str]]
    priority: Optional[str]
    deadline: Optional[int]
    point: Optional[int]
    files: Optional[list[str]]
    note: Optional[str]
    comment: Optional[str]
    link: Optional[str]
    review_status: Optional[str]
    time_rush: Optional[int]
    is_in_sprint: Optional[bool]