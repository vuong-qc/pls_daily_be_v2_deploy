from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class MeetingMessage(StrEnum):
    NOT_FOUND = "Meeting not found"
    START_TIME_GTE_END_TIME = "Meeting date gte than noti date"
    CURRENT_STATUS_CANT_CHANGE = "Meeting current status can't change"
    REPEAT_TYPE_NOT_MATCH_DATE = "Meeting repeat type not match date"
    NOT_OWNER = "YOU ARE not owner"

class MeetingStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    START_TIME_GTE_END_TIME = status.HTTP_400_BAD_REQUEST
    CURRENT_STATUS_CANT_CHANGE = status.HTTP_400_BAD_REQUEST
    REPEAT_TYPE_NOT_MATCH_DATE = status.HTTP_400_BAD_REQUEST
    NOT_OWNER = status.HTTP_400_BAD_REQUEST

class MeetingException(HTTPException):
    def __init__(self, message:MeetingMessage, code:MeetingStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
