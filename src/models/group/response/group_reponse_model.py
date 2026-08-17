from typing import Optional

from pydantic import BaseModel
from beanie import PydanticObjectId
class GroupResponse(BaseModel):
    id: Optional[PydanticObjectId] = None
    type: str
    name: str
    parent_id: Optional[str] = None
    sub_type: Optional[str] = None
    created_by: Optional[str] = None
    parent_type: Optional[str] = None
    is_archived: Optional[bool] = False

class GroupSummaryResponseModel(GroupResponse):
    total: Optional[int] = None
    resolve: Optional[int] = None
    children: Optional[list["GroupSummaryResponseModel"]] = None