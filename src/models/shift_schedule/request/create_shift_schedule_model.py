from pydantic import BaseModel, Field
from src.enums.weekday_enum import WeekdayEnum

class CreateShiftScheduleModel(BaseModel):
    user_id: str
    start_time: int
    end_time: int
    weekday: WeekdayEnum