from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class WorkItemMessage(StrEnum):
    WORK_ITEM_NOT_FOUND = "Task not found"

class WorkItemStatusCode(IntEnum):
    WORK_ITEM_NOT_FOUND = status.HTTP_404_NOT_FOUND


class WorkItemException(HTTPException):
    def __init__(self, message:WorkItemMessage, code: WorkItemStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
