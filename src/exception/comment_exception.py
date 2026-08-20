from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class CommentMessage(StrEnum):
    NOT_FOUND = 'Comment Not Found'
    NOT_CREATOR = "Only creator can delete comment"


class CommentStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    NOT_CREATOR = status.HTTP_400_BAD_REQUEST


class CommentException(HTTPException):
    def __init__(self, message:CommentMessage, code:CommentStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )