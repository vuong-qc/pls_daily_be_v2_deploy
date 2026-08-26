from typing import Optional

from pydantic import BaseModel
from beanie import PydanticObjectId
from src.models.user.response.user_response_model import UserResponse
class GroupResponse(BaseModel):
    id: Optional[PydanticObjectId] = None
    type: str
    name: str
    parent_id: Optional[str] = None
    sub_type: Optional[str] = None
    created_by: Optional[str] = None
    parent_type: Optional[str] = None
    is_archived: Optional[bool] = False
    des: Optional[str] = None
    creator_model: Optional[UserResponse] = None

class GroupSummaryResponseModel(GroupResponse):
    total: Optional[int] = None
    resolve: Optional[int] = None
    not_resolved: Optional[int] = None
    children: Optional[list["GroupSummaryResponseModel"]] = None