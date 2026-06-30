from typing import Optional

from pydantic import BaseModel, model_validator
from datetime import datetime

from src.enums.session_status_enum import SessionStatusEnum


class CreateSessionModel(BaseModel):
    user_id: Optional[str] = None
    status: str = SessionStatusEnum.NEW
    list_task: list[str]
    start_time: datetime
    notes: str
    work_form: Optional[str] = None

    # @model_validator(mode='after')
    # def update_status_if_late(self) -> 'CreateSessionModel':
    #     now = datetime.now(self.start_time.tzinfo)
    #
    #     if self.start_time < now:
    #         self.status = SessionStatusEnum.LATE
    #
    #     return self