from typing import Optional
from pydantic import BaseModel, Field

class FilterMeetingModel(BaseModel):
    handler: Optional[list[str]] = None
    participant_ids: Optional[list[str]] = None
    accepted_participant_ids: Optional[list[str]] = None
    meeting_form: Optional[str] = None
    creator: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    is_in_meeting: Optional[list[str]] = None
    limit: int = Field(10, le=100)
    offset: int = 0