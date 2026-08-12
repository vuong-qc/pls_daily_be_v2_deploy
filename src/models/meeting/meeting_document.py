from typing import Optional
from src.models.user.user_document import UserDocument
from beanie import DocumentWithSoftDelete, Link
from pydantic import Field
from src.enums.meeting_status_enum import MeetingStatusEnum

class MeetingDocument(DocumentWithSoftDelete):
    creator: str
    title: str
    description: str
    handler: list[str]
    participant_ids: list[str]
    accepted_participant_ids: list[str] = Field(default_factory=list)
    meeting_form: str
    status: str = Field(default=MeetingStatusEnum.NEW.value)
    meeting_date: int
    notification_date: Optional[int] = None
    meeting_hour: Optional[str] = None
    repeat_type: str
    date_of_month: Optional[int] = None
    parent_id: Optional[str] = None
    participant_models: Optional[list[Link[UserDocument]]] = None
    handler_models: Optional[list[Link[UserDocument]]] = None
    creator_model: Optional[Link[UserDocument]] = None
    department_id: Optional[str] = None

    class Settings:
        name= 'meetings'