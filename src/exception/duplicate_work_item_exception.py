from enum import StrEnum
from fastapi import HTTPException


class DuplicateWorkItemMessage(StrEnum):
    SOURCE_NOT_FOUND = "Source work item not found"
    SOURCE_TYPE_NOT_SUPPORTED = "Source work item type is not supported"
    SOURCE_SCOPE_NOT_SUPPORTED = "Only work items inside a project sprint can be duplicated"
    DESTINATION_NOT_FOUND = "Destination not found"
    DESTINATION_SPRINT_REQUIRED = "Destination sprint is required"
    DESTINATION_FIELD_NOT_ALLOWED = "Destination field is not allowed for source type"
    DESTINATION_TYPE_MISMATCH = "Destination type does not match"
    DESTINATION_TREE_MISMATCH = "Destination ids do not belong to the same tree"
    NOT_HANDLER_DESTINATION_PROJECT = "User is not a handler of destination project"
    INVALID_SOURCE_TREE = "Source work item tree is invalid"


class DuplicateWorkItemException(HTTPException):
    def __init__(self, message: DuplicateWorkItemMessage, status: int = 400):
        super().__init__(
            detail=message,
            status_code=status
        )