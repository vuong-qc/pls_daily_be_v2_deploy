from pydantic import BaseModel, Field
from typing import Optional
from src.utils.datetime_util import DateTimeUtil

class CreateDocumentItem(BaseModel):
    group_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    type: str
    date_time: int = Field(default_factory=DateTimeUtil.current_milli_time)
    object_id: Optional[str] = None
    parent_type: Optional[str] = None
    created_by: Optional[str] = None