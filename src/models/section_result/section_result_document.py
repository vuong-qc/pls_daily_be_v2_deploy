from typing import Optional, Union

from beanie import DocumentWithSoftDelete, Indexed, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from src.models.user.user_document import UserDocument
from src.utils.datetime_util import DateTimeUtil


class SectionResultDocument(DocumentWithSoftDelete):
    report_id: Indexed(str)
    section_item_id: Indexed(str)
    value: Optional[Union[float, str]] = None
    created_by: Optional[str] = None
    creator_model: Optional[Link[UserDocument]] = None
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    class Settings:
        name = "section_results"
        indexes = [
            IndexModel(
                [("report_id", ASCENDING), ("section_item_id", ASCENDING)],
                unique=True,
            ),
        ]
