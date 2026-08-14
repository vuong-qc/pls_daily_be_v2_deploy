from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional
from src.enums.session_status_enum import SessionStatusEnum


class FilterCheckInSessionModel(BaseModel):
    start_time: datetime
    status: Optional[list[SessionStatusEnum]] = None

class FilterSessionModel(BaseModel):
    status: Optional[list[SessionStatusEnum]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    user_id: Optional[str] = None
    offset: int = 0
    limit: int = Field(10,le=100)

class FilterSessionByDateRangeModel(BaseModel):
    start_time: str
    end_time: str
    user_id:  str
    checkin_late: Optional[bool] = None
    checkout_late: Optional[bool] = None
    arrival_status: Optional[str] = None
    departure_status: Optional[str] = None
    evaluate_session: Optional[str] = None
    work_form: Optional[str] = None