from typing import Optional

from pydantic import BaseModel

class UpdateMeetingModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    handler: Optional[list[str]] = None
    participant_ids: Optional[list[str]] = None
    accepted_participant_ids: Optional[list[str]] = None
    meeting_form: Optional[str] = None
    status: Optional[str] = None
    meeting_date: Optional[int] = None
    notification_date: Optional[int] = None
    meeting_hour: Optional[str] = None
    repeat_type: Optional[str] = None
    date_of_month: Optional[int] = None
    parent_id: Optional[int] = None
