from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class NotificationMessage(StrEnum):
    NOT_FOUND = "Notification not found"
    NOT_OWNER = "Notification owner is not matched"
    START_TIME_GTE_END_TIME = "Start time is greater than equal end time"
class NotificationStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    START_TIME_GTE_END_TIME = status.HTTP_400_BAD_REQUEST
    NOT_OWNER = status.HTTP_400_BAD_REQUEST

class NotificationException(HTTPException):
    def __init__(self, message:NotificationMessage, code:NotificationStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
