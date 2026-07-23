from enum import StrEnum

class MeetingStatusEnum(StrEnum):
    DONE = "DONE"
    NEW = "NEW"
    CANCELED = "CANCELED"
    IN_PROGRESS = "IN_PROGRESS"