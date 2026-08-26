from pydantic import BaseModel
from typing import Optional
from src.enums.group_type_enum import GroupType

class UpdateGroupModel(BaseModel):
    type: Optional[GroupType] = None
    name: Optional[str] = None
    is_archived: Optional[bool] = None
    des: Optional[str] = None