from typing import Optional
from pydantic import BaseModel

class CreateMeetingModel(BaseModel):
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
