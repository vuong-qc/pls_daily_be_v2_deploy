from typing import Optional
from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId

class DocumentResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    owner_id: Optional[str] = None
    parent_id: str
    evaluate: Optional[str] = None
    check: Optional[bool] = None