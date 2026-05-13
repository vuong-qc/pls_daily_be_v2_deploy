from pydantic import BaseModel, Field
from src.utils.datetime_util import DateTimeUtil

class ChangePasswordModel(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)