from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from typing import Optional
from src.models.user.response.user_response_model import UserResponse

class VersionResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    creator_id: str
    type: str
    object_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    version: Optional[str] = None
    creator_model: Optional[UserResponse] = None
    updator_model: Optional[UserResponse] = None
    updator_id: Optional[str] = None
    created_at: int
    updated_at: int