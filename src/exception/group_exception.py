from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class GroupMessage(StrEnum):
    NOT_FOUND = "Group not found"
    NOT_CREATOR = 'Only creator of group is allowed to modify this group'
class GroupStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    NOT_CREATOR = status.HTTP_400_BAD_REQUEST

class GroupException(HTTPException):
    def __init__(self, message:GroupMessage, code:GroupStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
