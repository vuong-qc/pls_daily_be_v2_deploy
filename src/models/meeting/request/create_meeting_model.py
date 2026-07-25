from typing import Optional
from src.enums.meeting_repeat_type import MeetingRepeatType
from pydantic import BaseModel, model_validator, Field


class CreateMeetingModel(BaseModel):
    creator: str
    title: str
    description: str
    handler: list[str]
    participant_ids: list[str]
    meeting_form: str
    meeting_date: int
    notification_date: Optional[int] = None
    meeting_hour: Optional[str] = None
    repeat_type: str
    date_of_month: Optional[int] = Field(default=None, le=31)
    parent_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_meeting_date(self):
        if self.repeat_type == MeetingRepeatType.MONTHLY:
            if self.date_of_month is None or not (1 <= self.date_of_month <= 31):
                raise ValueError("Meeting date must be between 1 and 31, repeat type is set to MONTHLY")

        else:
            self.date_of_month = None

        return self