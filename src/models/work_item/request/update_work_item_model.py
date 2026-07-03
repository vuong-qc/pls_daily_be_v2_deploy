from typing import Optional

from pydantic import BaseModel

class UpdateWorkItemModel(BaseModel):
    updated_at: Optional[int] = None
    parent: Optional[str] = None
    assigned_id: Optional[list[str]] = None
    start: Optional[int] = None
    end: Optional[int] = None
    duration: Optional[int] = None
    handler_id: Optional[list[str]] = None
    priority: Optional[str] = None
    deadline: Optional[int] = None
    point: Optional[int] = None
    files: Optional[list[str]] = None
    note: Optional[str] = None
    comment: Optional[str] = None
    link: Optional[str] = None
    review_status: Optional[str] = None
    time_rush: Optional[int] = None
    is_in_sprint: Optional[bool] = None
    project: Optional[str] = None
    group: Optional[str] = None
    sprint: Optional[str] = None
    task: Optional[str] = None
    des: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None

    screen: Optional[str] = None
    action: Optional[str] = None
    blame: Optional[str] = None
    extra_info: Optional[str] = None
    platform: Optional[str] = None
    device: Optional[str] = None
    device_version: Optional[str] = None
    project_version: Optional[str] = None