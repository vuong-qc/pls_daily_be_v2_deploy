from pydantic import BaseModel, Field
from typing import Optional
from src.enums.document_type_enum import DocumentTypeEnum

class FilterDocumentItem(BaseModel):
    group_id: Optional[list[str]] = None
    object_id: Optional[list[str]] = None
    type: Optional[list[DocumentTypeEnum]] = None
    limit: int = Field(10, le=100)
    offset: int = 0
    parent_type: Optional[list[str]] = None
    is_archived: Optional[bool] = None
    is_checked: Optional[bool] = None
    is_urgent: Optional[bool] = None
    ftf: Optional[bool] = None
    is_closed: Optional[bool] = None
    start_deadline: Optional[int] = None
    end_deadline: Optional[int] = None