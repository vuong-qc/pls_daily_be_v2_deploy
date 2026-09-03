from enum import IntEnum, StrEnum

from fastapi import HTTPException, status


class SectionMessage(StrEnum):
    NOT_FOUND = "Section Not Found"
    INVALID_PARENT = "Section Parent Invalid"
    INVALID_VALUE_TYPE = "Section Value Type Invalid"
    TEMPLATE_NOT_EDITABLE = "Template Must Be Draft"
    INVALID_TYPE = "Section Type Invalid"


class SectionStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    INVALID_PARENT = status.HTTP_400_BAD_REQUEST
    INVALID_VALUE_TYPE = status.HTTP_400_BAD_REQUEST
    TEMPLATE_NOT_EDITABLE = status.HTTP_400_BAD_REQUEST
    INVALID_TYPE = status.HTTP_400_BAD_REQUEST


class SectionException(HTTPException):
    def __init__(self, message: SectionMessage, code: SectionStatusCode):
        super().__init__(detail=message, status_code=code)
