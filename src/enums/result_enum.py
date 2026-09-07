from enum import StrEnum


class ResultStatus(StrEnum):
    DISPLAY = "DISPLAY"
    CLOSED = "CLOSED"

class ResultType(StrEnum):
    REPORT = "REPORT"

class ResultObjectType(StrEnum):
    USER = "USER"
    DEPARTMENT = "DEPARTMENT"
