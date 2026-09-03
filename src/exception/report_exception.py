from enum import IntEnum, StrEnum

from fastapi import HTTPException, status


class ReportMessage(StrEnum):
    NOT_FOUND = "Report Not Found"
    FORBIDDEN = "No Permission For Report"
    TEMPLATE_NOT_PUBLIC = "Template Must Be Public"
    USER_NOT_FOUND = "Shared User Not Found"
    DEPARTMENT_NOT_FOUND = "Shared Department Not Found"
    NOT_EDITABLE = "Only Draft Report Can Be Modified"


class ReportStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    FORBIDDEN = status.HTTP_403_FORBIDDEN
    TEMPLATE_NOT_PUBLIC = status.HTTP_400_BAD_REQUEST
    USER_NOT_FOUND = status.HTTP_404_NOT_FOUND
    DEPARTMENT_NOT_FOUND = status.HTTP_404_NOT_FOUND
    NOT_EDITABLE = status.HTTP_400_BAD_REQUEST


class ReportException(HTTPException):
    def __init__(self, message: ReportMessage, code: ReportStatusCode):
        super().__init__(detail=message, status_code=code)
