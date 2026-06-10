from enum import StrEnum

class GroupType(StrEnum):
    PROJECT = "PROJECT"
    TAG = "TAG"
    TC = 'TC'
    QA = 'QA'
    DOCUMENT = 'DOCUMENT'
    BUG = 'BUG'
    CHECKLIST = 'CHECKLIST'
    TODO = 'TODO'

class GroupSubType(StrEnum):
    SUB_DOCUMENT = "SUB_DOCUMENT"