from enum import IntEnum, StrEnum

from fastapi import HTTPException, status


class VersionMessage(StrEnum):
    NOT_FOUND = "Version not found"
    INVALID_SCOPE = "Invalid version scope"
    OBJECT_ID_REQUIRED = "Object id is required for this version type"
    OBJECT_ID_NOT_ALLOWED = "Object id is not allowed for personal version"
    PROJECT_NOT_FOUND = "Project not found"
    DEPARTMENT_NOT_FOUND = "Department not found"
    USER_NOT_FOUND = "User not found"
    FORBIDDEN = "No permission for version"
    EMPTY_UPDATE = "At least one update field is required"
    TITLE_REQUIRED = "Title must not be blank"


class VersionStatusCode(IntEnum):
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    INVALID_SCOPE = status.HTTP_422_UNPROCESSABLE_CONTENT
    OBJECT_ID_REQUIRED = status.HTTP_422_UNPROCESSABLE_CONTENT
    OBJECT_ID_NOT_ALLOWED = status.HTTP_422_UNPROCESSABLE_CONTENT
    PROJECT_NOT_FOUND = status.HTTP_404_NOT_FOUND
    DEPARTMENT_NOT_FOUND = status.HTTP_404_NOT_FOUND
    USER_NOT_FOUND = status.HTTP_404_NOT_FOUND
    FORBIDDEN = status.HTTP_403_FORBIDDEN
    EMPTY_UPDATE = status.HTTP_422_UNPROCESSABLE_CONTENT
    TITLE_REQUIRED = status.HTTP_422_UNPROCESSABLE_CONTENT


class VersionException(HTTPException):
    def __init__(self, message: VersionMessage, code: VersionStatusCode):
        super().__init__(status_code=code, detail=message)
