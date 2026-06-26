from enum import StrEnum

class DocumentParentType(StrEnum):
    SPRINT = 'SPRINT'
    PROJECT = 'PROJECT'

class WorkItemType(StrEnum):
    TASK = 'TASK'
    SUBTASK = 'SUBTASK'
    SPRINT = 'SPRINT'
    PROJECT = 'PROJECT'
    BUG = 'BUG'
    BACKLOG = 'BACKLOG'
    STORY = 'STORY'
    TODO = 'TODO'