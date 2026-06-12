from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class ChatbotTokenMessage(StrEnum):
    NOT_FOUND = 'ChatbotToken Not Found'

class ChatbotTokenStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND


class ChatbotTokenException(HTTPException):
    def __init__(self, message:ChatbotTokenMessage, code:ChatbotTokenStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )