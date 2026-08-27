from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class TemplateMessage(StrEnum):
    NOT_FOUND = 'Template Not Found'
    STATUS_INVALID = 'Status Invalid, PUBLIC/DISABLED can not change to DRAFT'
    NOT_OWNER = 'Not Owner of Template'
    CAN_NOT_MODIFY = 'PUBLIC/DISABLED template Can Not be Modify'

class TemplateStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    STATUS_INVALID = status.HTTP_400_BAD_REQUEST
    NOT_OWNER = status.HTTP_400_BAD_REQUEST
    CAN_NOT_MODIFY = status.HTTP_400_BAD_REQUEST

class TemplateException(HTTPException):
    def __init__(self, message:TemplateMessage, code:TemplateStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )