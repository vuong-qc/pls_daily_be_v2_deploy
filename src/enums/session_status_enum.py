from enum import StrEnum

class SessionStatusEnum(StrEnum):
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    CANCELED = 'CANCELED'
    DONE = 'DONE'
    LATE ='LATE'

class ArrivalStatusEnum(StrEnum):

    ARRIVE_LATE = "ARRIVE_LATE"
    ARRIVE_ON_TIME = "ARRIVE_ON_TIME"
    LOGTIME_TIME = "LOGTIME_TIME"

class DepartmentStatusEnum(StrEnum):
    LEAVE_EARLY = "LEAVE_EARLY"
    LEAVE_ON_TIME = "LEAVE_ON_TIME"
    OT = "OT"
    LOGTIME_TIME ="LOGTIME_TIME"

class WorkFormEnum(StrEnum):
    WFH = "WFH"
    IN_OFFICE = "IN_OFFICE"