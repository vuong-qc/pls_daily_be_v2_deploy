from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from typing import Optional

from src.models.document_result.response.document_result_response import DocumentResultResponse


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    group_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    type: str
    date_time: int
    object_id: Optional[str] = None
    result: Optional[DocumentResultResponse] = None
    created_by: Optional[str] = None
    is_archived: Optional[bool] = False
    is_checked: Optional[bool] = False
    is_urgent: Optional[bool] = False