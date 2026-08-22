from enum import StrEnum
class BugStatusEnum(StrEnum):
    NEW = "NEW"
    FIXING = "FIXING"
    VERIFIED = "VERIFIED"
    FIXED = "FIXED"
    NO_HANDLE = "NO_HANDLE"
    LATER = "LATER"
    DUPLICATE = "DUPLICATE"
    UNKNOWN = "UNKNOWN"
    CONFIRMED = "CONFIRMED"
    NEW_FUNCTION = "NEW_FUNCTION"