from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class SprintMessage(StrEnum):
    NOT_FOUND = "Sprint not found"
    NOT_HANDLER_PR0JECT = "Only handlers of project can add sprint"
    DELETE_NOT_MATCH_TYPE = "Type Item must be SPRINT to be deleted"
class SprintStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    NOT_HANDLER_PR0JECT = status.HTTP_400_BAD_REQUEST
    DELETE_NOT_MATCH_TYPE = status.HTTP_400_BAD_REQUEST

class SprintException(HTTPException):
    def __init__(self, message:SprintMessage, code: SprintStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
