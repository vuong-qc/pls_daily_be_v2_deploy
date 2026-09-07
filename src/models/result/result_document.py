from typing import Optional
from beanie import DocumentWithSoftDelete
from pydantic import Field
from src.utils.datetime_util import DateTimeUtil


class ResultDocument(DocumentWithSoftDelete):
    parent_id: str
    type: str
    object_id: str
    object_type: str
    # status: str
    closed_by: Optional[list[str]] = []
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    class Settings:
        name = "results"
        indexes = [
            "parent_id",
            "object_id",
            "type",
            "object_type",
            "status",
        ]