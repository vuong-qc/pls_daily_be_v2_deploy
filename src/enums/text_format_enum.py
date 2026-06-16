from enum import StrEnum

class TextFormatEnum(StrEnum):
    CHECKIN = "*{time}*, {user} checked in!"
    TASK_HEADER = "- *Task*:"
    TASK_PREFIX = " - "
    REMIND_CHECK_IN = "Nhắc nhở {user} chưa check in"
    REMIND_CHECK_OUT = "Nhắc nhở {user} quên check out"
    TASK_EMPTY = "Không chọn task"
    NOTE = '- *Ghi chú*:'
    NEWLINE = '\n'
    SPACE = ' '