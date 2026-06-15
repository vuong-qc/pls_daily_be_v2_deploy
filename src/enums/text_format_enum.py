from enum import StrEnum

class TextFormatEnum(StrEnum):
    CHECKIN = "{time}, {user} checked in!"
    TASK_HEADER = "Task:"
    TASK_PREFIX = " - "
    REMIND_CHECK_IN = "Remind {user} check in"
    REMIND_CHECK_OUT = "Remind {user} check out"