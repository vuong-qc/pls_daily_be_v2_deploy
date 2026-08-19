from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict

from src.models.user.response.user_response_model import UserResponse
from typing import Optional

class EvaluateResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    creator_id: str
    assigned_id: str
    update_user: Optional[str] = None
    title: str
    description: Optional[str]= None
    value: Optional[int] = None
    point: Optional[int] = None
    updated_at: int
    created_at: int
    creator_model: Optional[UserResponse] = None
    assigned_model: Optional[UserResponse] = None
    updated_model: Optional[UserResponse] = None