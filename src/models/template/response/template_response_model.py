from typing import Optional
from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from src.models.user.response.user_response_model import UserResponse

class TemplateResponseModel(BaseModel):
    model_config =  ConfigDict(from_attributes=True)
    id: PydanticObjectId
    created_by: str
    creator_model: Optional[UserResponse] = None
    position: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    created_at: int
    updated_at: int
    group: str