from enum import StrEnum

class ErrorResponseEnum(StrEnum):
    NOT_FOUND = "Not Found"
    INTERNAL_ERROR = "Internal Error"
    UNAUTHORIZED = "Unauthorized"