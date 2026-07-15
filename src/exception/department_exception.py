from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class DepartmentMessage(StrEnum):
    NOT_FOUND = 'Department Not Found'


class DepartmentStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND


class DepartmentException(HTTPException):
    def __init__(self, message:DepartmentMessage, code:DepartmentStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )