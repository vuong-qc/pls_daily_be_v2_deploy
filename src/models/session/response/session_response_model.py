from typing import Optional

from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from datetime import datetime
from src.models.user.response.user_response_model import UserResponse
from src.models.task.response.task_response_model import TaskResponse
from src.models.session.session_view import SessionInGroup

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
    checkin_late: Optional[bool] = None
    checkout_late: Optional[bool] = None
    arrival_status: Optional[str] = None
    departure_status: Optional[str] = None
    evaluate_session: Optional[str] = None

class SessionTaskResponse(SessionInGroup):
    list_tasks_data: Optional[list[TaskResponse]] = None
