from typing import Optional
from src.models.user.user_document import UserDocument
from beanie import DocumentWithSoftDelete, Link

class MeetingDocument(DocumentWithSoftDelete):
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
    parent_id: Optional[int] = None
    participant_models: list[Link[UserDocument]]
    handler_models: list[Link[UserDocument]]
    creator_model: Link[UserDocument]

    class Settings:
        name= 'meetings'