from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class EvaluateMessage(StrEnum):
    NOT_FOUND = 'Evaluate Not Found'
    CREATOR_NOT_MATCH = 'Creator Not Match'

class EvaluateStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    CREATOR_NOT_MATCH = status.HTTP_400_BAD_REQUEST


class EvaluateException(HTTPException):
    def __init__(self, message:EvaluateMessage, code:EvaluateStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )