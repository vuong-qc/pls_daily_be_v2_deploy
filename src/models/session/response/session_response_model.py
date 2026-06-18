from typing import Optional

from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from datetime import datetime
from src.models.user.response.user_response_model import UserResponse
from src.models.task.response.task_response_model import TaskResponse
class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    user_id: str
    status: str
    list_task: list[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str
    user: Optional[UserResponse] = None
    list_tasks_data: Optional[list[TaskResponse]] = None
    checkin: Optional[bool] = None
    checkout: Optional[bool] = None
    note_result: Optional[str] = None
    work_form: Optional[str] = None