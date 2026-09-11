from enum import StrEnum

class TaskPriorityEnum(StrEnum):
    HIGH = "HIGH"
    FTF = "FTF"
    LOW = "LOW"
    MEDIUM = "MEDIUM"

class BugPriorityEnum(StrEnum):
    HIGH = "HIGH"
    FTF = "FTF"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    URGENT = "URGENT"