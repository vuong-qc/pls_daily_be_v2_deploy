from pydantic import BaseModel, ConfigDict
from typing import Optional
from beanie import PydanticObjectId
from src.models.user.response.user_response_model import UserResponse

class CommentResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    object_id: str
    parent_id: Optional[str] = None
    content: str
    ancestors: list[str] = []
    reply_count: int = 0
    mentions: list[str] = []
    created_at : int
    updated_at : int
    creator: UserResponse
    mention_data: Optional[list[dict]] = None