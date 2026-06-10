from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional, Annotated
from pydantic.functional_validators import BeforeValidator
from src.utils.datetime_util import DateTimeUtil
from src.enums.user_status_enum import UserStatusEnum

PyObjectId = Annotated[str, BeforeValidator(str)]

class CreateUserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    dob: Optional[datetime] = None
    avt: str = ""
    email: str
    name: str
    phone: str
    password: str = Field(..., max_length=72)
    roles: List[int]
    require_pass_update: bool = True
    status: int = UserStatusEnum.ACTIVE.value
    gender: int
    address: Optional[str] = None
    traineeStatus: int
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "Nguyen Van A",
                "phone": "0912345678",
                "password": "abc12345",
                "roles": [1],
                "gender": 1,
                "traineeStatus": 0,
            }
        }
    )
