from enum import StrEnum

class DocumentResultEvaluate(StrEnum):
    PASS = 'PASS'
    FAIL = 'FAIL'
    PARTIAL_PASS = 'PARTIAL_PASS'
    SKIP = 'SKIP'
