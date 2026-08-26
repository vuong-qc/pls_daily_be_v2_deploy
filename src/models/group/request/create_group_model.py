from typing import Optional

from pydantic import BaseModel
from src.enums.group_type_enum import GroupType, GroupSubType

class CreateGroupModel(BaseModel):
    type: GroupType
    name: str
    parent_id: Optional[str] = None
    sub_type: Optional[GroupSubType] = None
    created_by: Optional[str] = None
    parent_type: Optional[str] = None
    is_archived: Optional[bool] = None
    des: Optional[str] = None