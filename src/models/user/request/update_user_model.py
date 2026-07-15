from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from src.enums.user_status_enum import UserStatusEnum
from datetime import datetime
from src.utils.datetime_util import DateTimeUtil

class UpdateUserModel(BaseModel):
    dob: Optional[datetime] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[int] = None
    avt: Optional[str] = None
    roles: Optional[list[int]] = None
    status: Optional[UserStatusEnum] = None
    traineeStatus: Optional[int] = None
    password: Optional[str] = None
    address: Optional[str] = None
    department: Optional[list[str]] = None
    daily_checkin: Optional[bool] = None
    nickname: Optional[str] = None


    model_config = ConfigDict(extra='ignore')

class UpdateProfileModel(BaseModel):
    address: Optional[str] = None
    dob: Optional[datetime] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[int] = None
    avt: Optional[str] = None
    password: Optional[str] = None
    daily_checkin: Optional[bool] = None
    department: Optional[list[str]] = None
    nickname: Optional[str] = None
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)