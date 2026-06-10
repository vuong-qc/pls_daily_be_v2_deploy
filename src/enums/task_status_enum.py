from enum import StrEnum

class TaskStatusEnum(StrEnum):
    DONE = 'DONE'
    CANCELED = 'CANCELED'
    NEW = 'NEW'
    PROCESSING = 'PROCESSING'