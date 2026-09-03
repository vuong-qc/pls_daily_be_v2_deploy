from typing import Optional

from beanie import DocumentWithSoftDelete
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from src.utils.datetime_util import DateTimeUtil


class SectionDocument(DocumentWithSoftDelete):
    type: str
    parent_id: str
    position: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    value_type: Optional[str] = None
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    class Settings:
        name = "sections"
        indexes = [
            IndexModel([
                ("parent_id", ASCENDING),
                ("type", ASCENDING),
                ("position", ASCENDING),
            ]),
        ]
