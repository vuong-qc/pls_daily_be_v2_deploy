from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class GroupMessage(StrEnum):
    NOT_FOUND = "Group not found"
class GroupStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND

class GroupException(HTTPException):
    def __init__(self, message:GroupMessage, code:GroupStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
