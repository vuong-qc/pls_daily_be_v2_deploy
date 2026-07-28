import pymongo
from pymongo import IndexModel
from beanie import DocumentWithSoftDelete
from pydantic import Field

from src.enums.shift_schedule_status import ShiftScheduleStatus
from src.utils.datetime_util import DateTimeUtil


class ShiftScheduleDocument(DocumentWithSoftDelete):
    user_id: str
    status: str = ShiftScheduleStatus.ACTIVE
    start_time: int
    end_time: int
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    weekday: int

    class Settings:
        name = "shift_schedule"
        indexes = [
            "user_id",
            "weekday",
            "status",
            IndexModel(["user_id", "weekday"]),
            IndexModel(["weekday", "status"]),
            IndexModel(["user_id", "status", "weekday"]),
        ]