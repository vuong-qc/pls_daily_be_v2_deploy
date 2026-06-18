from fastapi import status, HTTPException
from enum import StrEnum, IntEnum

class SessionStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    TASK_SUBTASK_TYPE_NOT_MATCH = status.HTTP_400_BAD_REQUEST
    NOT_OWNER = status.HTTP_400_BAD_REQUEST
    START_GTE_END_TIME = status.HTTP_400_BAD_REQUEST

class SessionMessage(StrEnum):
    NOT_FOUND = 'Session not found'
    TASK_SUBTASK_TYPE_NOT_MATCH = 'Task/subtask type not match'
    NOT_OWNER = 'Not owner of session'
    START_GTE_END_TIME = 'Start time >= end time'

class SessionException(HTTPException):
    def __init__(self, message: SessionMessage, code: SessionStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )