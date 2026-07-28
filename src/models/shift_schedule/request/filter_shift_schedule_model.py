from typing import Optional
from src.enums.shift_schedule_status import ShiftScheduleStatus
from src.enums.weekday_enum import WeekdayEnum
from pydantic import BaseModel, Field

class FilterShiftScheduleModel(BaseModel):
    user_id: Optional[str] = None
    weekday: Optional[WeekdayEnum] = None
    status: Optional[ShiftScheduleStatus] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    offset: Optional[int] = Field(default=None)
    limit: Optional[int] = Field(default=None, le=100)