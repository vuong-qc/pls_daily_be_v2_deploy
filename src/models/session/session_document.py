from typing import Optional

from beanie import DocumentWithSoftDelete, Link
from datetime import datetime
from pydantic import field_validator
from zoneinfo import ZoneInfo
from src.configs import settings
from src.models.user.user_document import UserDocument
class SessionDocument(DocumentWithSoftDelete):
    user_id: str
    status: str
    list_task: list[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str
    user: Optional[Link[UserDocument]] = None
    checkin: Optional[bool] = None
    checkout: Optional[bool] = None
    note_result: Optional[str] = None
    work_form: Optional[str] = None

    @field_validator('start_time', mode='after')
    @classmethod
    def validate_start_time(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        # Nếu chuỗi truyền lên có Z, Pydantic v2 sẽ nhận diện được v.tzinfo
        # Nếu chưa có múi giờ, ta ép nó về UTC (vì chữ Z đại diện cho UTC)
        if v.tzinfo is None:
            v = v.replace(tzinfo=ZoneInfo("UTC"))

        # Hoặc bạn có thể chuyển hẳn nó sang múi giờ Asia/Ho_Chi_Minh tại đây:
        return v.astimezone(ZoneInfo(settings.TZ))
