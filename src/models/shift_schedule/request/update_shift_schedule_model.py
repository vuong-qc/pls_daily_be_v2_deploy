from typing import Optional

from pydantic import BaseModel, Field
from src.enums.weekday_enum import WeekdayEnum
from src.enums.shift_schedule_status import ShiftScheduleStatus

class UpdateShiftScheduleModel(BaseModel):
    start_time: Optional[int]
    end_time: Optional[int]
    weekday: Optional[WeekdayEnum] = None
    status: Optional[ShiftScheduleStatus] = None