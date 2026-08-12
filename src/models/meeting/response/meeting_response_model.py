from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from src.models.user.response.user_response_model import UserResponse
from typing import Optional

class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    creator: str
    title: str
    description: str
    handler: list[str]
    participant_ids: list[str]
    accepted_participant_ids: list[str]
    meeting_form: str
    status: str
    meeting_date: int
    notification_date: Optional[int] = None
    meeting_hour: Optional[str] = None
    repeat_type: str
    date_of_month: Optional[int] = None
    parent_id: Optional[str] = None
    participant_models: Optional[list[UserResponse]] = None
    handler_models: Optional[list[UserResponse]] = None
    creator_model: Optional[UserResponse] = None
    department_id: Optional[str] = None