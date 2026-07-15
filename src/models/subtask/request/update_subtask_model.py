from pydantic import BaseModel
from src.enums.task_status_enum import TaskStatusEnum
from typing import Optional

class UpdateSubtaskModel(BaseModel):
    title: Optional[str] =None
    type: Optional[str] = None
    des: Optional[str] =None
    status: Optional[TaskStatusEnum] = None
    duration: Optional[int] = None
    time_rush: Optional[int] = None
    review_status: Optional[str] = None
    updated_at: Optional[int] = None
    parent: Optional[str] = None
    session_id: Optional[str] = None


