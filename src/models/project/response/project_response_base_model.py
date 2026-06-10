from typing import Optional

from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId

class ProjectInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    title: str
    owner_id: Optional[str] = None
    type: str
    status: str
    parent: Optional[str] = None
    des: Optional[str] = None
