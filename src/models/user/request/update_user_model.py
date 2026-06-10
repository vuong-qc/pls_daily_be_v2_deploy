from pydantic import BaseModel, ConfigDict
from typing import Optional
from src.enums.user_status_enum import UserStatusEnum
from datetime import datetime

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

    model_config = ConfigDict(extra='ignore')