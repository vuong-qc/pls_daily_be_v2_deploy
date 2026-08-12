from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class PlanMessage(StrEnum):
    NOT_FOUND = 'Plan Not Found'

class PlanStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND


class PlanException(HTTPException):
    def __init__(self, message:PlanMessage, code:PlanStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )