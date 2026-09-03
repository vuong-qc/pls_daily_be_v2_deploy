from enum import StrEnum


class SectionTypeEnum(StrEnum):
    SECTION = "SECTION"
    ITEM = "ITEM"


class SectionValueTypeEnum(StrEnum):
    NUMBER = "NUMBER"
    TEXT = "TEXT"
    PROGRESS = "PROGRESS"
