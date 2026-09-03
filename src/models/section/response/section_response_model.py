from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class SectionResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    type: str
    parent_id: str
    position: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    value_type: Optional[str] = None
    created_at: int
    updated_at: int
    items: list["SectionResponseModel"] = Field(default_factory=list)
