from fastapi import HTTPException, status
from enum import StrEnum, IntEnum

class DocumentMessage(StrEnum):
    NOT_FOUND = 'Document Not Found'
    PARENT_TYPE_NOT_MATCH = 'Parent Type Not Match'
    NOT_CREATOR = 'Creator of Document Not Match'
    TASKER_NOT_MATCH_SPRINT = 'Only Tasker of sprint can add Q&A'
    NOT_ENOUGH_DATA = 'Not enough data TO validate data, missing: parent_id/ created_by/ object_id'
    DOCUMENT_RESULT_NOT_FOUND = 'Document Result Not Found'
    CANT_ASSIGN_FTF = "Can't assign FtF, total == 5"

class DocumentStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    PARENT_TYPE_NOT_MATCH = status.HTTP_400_BAD_REQUEST
    NOT_CREATOR = status.HTTP_400_BAD_REQUEST
    TASKER_NOT_MATCH_SPRINT = status.HTTP_400_BAD_REQUEST
    NOT_ENOUGH_DATA = status.HTTP_400_BAD_REQUEST
    DOCUMENT_RESULT_NOT_FOUND = status.HTTP_404_NOT_FOUND
    CANT_ASSIGN_FTF = status.HTTP_400_BAD_REQUEST

class DocumentException(HTTPException):
    def __init__(self, message:DocumentMessage, code:DocumentStatusCode):
        super().__init__(
            detail=message,
            status_code=code
        )