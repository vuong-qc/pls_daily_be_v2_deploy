from enum import IntEnum, StrEnum

from fastapi import HTTPException, status


class SectionResultMessage(StrEnum):
    ITEM_NOT_FOUND = "Section Item Not Found"
    ITEM_NOT_BELONG = "Section Item Does Not Belong To Report"
    INVALID_VALUE = "Section Result Value Invalid"


class SectionResultStatusCode(IntEnum):
    ITEM_NOT_FOUND = status.HTTP_404_NOT_FOUND
    ITEM_NOT_BELONG = status.HTTP_400_BAD_REQUEST
    INVALID_VALUE = status.HTTP_400_BAD_REQUEST


class SectionResultException(HTTPException):
    def __init__(self, message: SectionResultMessage, code: SectionResultStatusCode):
        super().__init__(detail=message, status_code=code)
