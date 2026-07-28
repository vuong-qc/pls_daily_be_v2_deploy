from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class ShiftScheduleMessage(StrEnum):
    NOT_FOUND = 'ShiftSchedule Not Found'
    END_LTE_START = 'End time LTE Start time'
    CONFLICT = 'ShiftSchedule Conflict in same weekday'


class ShiftScheduleStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    END_LTE_START = status.HTTP_400_BAD_REQUEST
    CONFLICT = status.HTTP_400_BAD_REQUEST

class ShiftScheduleException(HTTPException):
    def __init__(self, message:ShiftScheduleMessage, code:ShiftScheduleStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )