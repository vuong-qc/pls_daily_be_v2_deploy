from typing import Optional, Union

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict

from src.models.user.response.user_response_model import UserResponse


class SectionResultResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    report_id: str
    section_item_id: str
    value: Optional[Union[float, str]] = None
    created_by: Optional[str] = None
    creator_model: Optional[UserResponse] = None
    created_at: int
    updated_at: int
