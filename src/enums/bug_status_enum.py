from enum import StrEnum
class BugStatusEnum(StrEnum):
    NEW = "NEW"
    FIXING = "FIXING"
    VERIFIED = "VERIFIED"
    FIXED = "FIXED"