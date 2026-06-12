from enum import StrEnum

class TextFormatEnum(StrEnum):
    CHECKIN = "{time}, {user} checked in!"
    TASK_HEADER = "Task:"
    TASK_PREFIX = " - "