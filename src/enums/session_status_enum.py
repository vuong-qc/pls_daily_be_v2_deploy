from enum import StrEnum

class SessionStatusEnum(StrEnum):
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    CANCELED = 'CANCELED'
    DONE = 'DONE'