from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pymongo
from beanie import DocumentWithSoftDelete, Link
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel

if TYPE_CHECKING:
    from src.models.user.user_document import UserDocument

class WorkItemDocument(DocumentWithSoftDelete):
    type: str
    title: str
    des: Optional[str] = None
    status: str = None
    created_at: int
    updated_at: int
    parent: Optional[str] = None
    owner_id: Optional[str] = None
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
    owner: Optional[Link[UserDocument]] = None
    assignee: Optional[list[Link[UserDocument]]] = None
    handler: Optional[list[Link[UserDocument]]] = None
    session_id: Optional[str] = None
    review_status: Optional[str] = None
    time_rush: Optional[int] = None
    is_in_sprint: Optional[bool] = None
    parent_model: Optional[Link[WorkItemDocument]] = None
    project: Optional[str] = None
    group: Optional[str] = None
    sprint: Optional[str] = None
    task: Optional[str] = None
    explanation: Optional[str] = None
    expect_result: Optional[str] = None
    screen: Optional[str] = None
    action: Optional[str] = None
    blame: Optional[str] = None
    extra_info: Optional[str] = None
    platform: Optional[str] = None
    device: Optional[str] = None
    device_version: Optional[str] = None
    project_version: Optional[str] = None
    bug_type: Optional[str] = None
    department_id: Optional[str] = None

    class Settings:
        name = "work_items"
        indexes = [
            "project",
            "assigned_id",
            "parent",
            "type",
            IndexModel([("project", pymongo.ASCENDING), ("status", pymongo.ASCENDING)]),
            IndexModel([("status", pymongo.ASCENDING),("deadline", pymongo.ASCENDING)]),
            IndexModel([("type", pymongo.ASCENDING), ("created_at", pymongo.ASCENDING)]),
        ]


class SprintTaskStatsResult(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    total_tasks: int
    target_status_tasks: int