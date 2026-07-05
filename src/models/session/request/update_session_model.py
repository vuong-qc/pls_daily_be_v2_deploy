from datetime import datetime
from typing import Optional
from src.enums.task_status_enum import TaskStatusEnum
from src.enums.session_status_enum import SessionStatusEnum

from pydantic import BaseModel

class UpdateSessionModel(BaseModel):
    status: Optional[SessionStatusEnum] = None
    list_task: Optional[list[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    work_form: Optional[str] = None
    note_result: Optional[str] = None

class UpdateSubTaskModel(BaseModel):
    status: TaskStatusEnum
    id: str

class CheckoutModel(BaseModel):
    list_subtasks: list[UpdateSubTaskModel]
    end_time: Optional[datetime] = None
    note_result: Optional[str] = None
    checkout_late: Optional[bool] = None
