from enum import StrEnum

class SprintStatusEnum(StrEnum):
    DONE = 'DONE'
    CANCELED = 'CANCELED'
    NEW = 'NEW'
    PROCESSING = 'PROCESSING'