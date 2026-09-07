from enum import StrEnum


class ReportTypeEnum(StrEnum):
    PERSONAL = "PERSONAL"
    DEPARTMENT = "DEPARTMENT"


class ReportStatusEnum(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
