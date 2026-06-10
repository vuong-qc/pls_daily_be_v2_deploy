from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class ProjectMessage(StrEnum):
    NOT_FOUND = "Project not found"
    NOT_HANDLER_PROJECT = "Only handler of project can add item"
    NOT_HAVE_HANDLER = ' Project does not have handler'
class ProjectStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    NOT_HANDLER_PROJECT = status.HTTP_400_BAD_REQUEST
    NOT_HAVE_HANDLER = status.HTTP_400_BAD_REQUEST

class ProjectException(HTTPException):
    def __init__(self, message:ProjectMessage, code:ProjectStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
