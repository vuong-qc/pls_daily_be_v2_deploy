from enum import StrEnum

class TaskStatusEnum(StrEnum):
    DONE = 'DONE'
    CANCELED = 'CANCELED'
    NEW = 'NEW'
    PROCESSING = 'PROCESSING'

class TaskPreviewStatusEnum(StrEnum):
    LATE = 'LATE'
    OK = "OK"
    GOOD = "GOOD"
    BUG = "BUG"
    BUG_AND_LATE = "BUG_AND_LATE"
    FAILED = "FAILED"
