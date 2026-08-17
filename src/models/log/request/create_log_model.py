from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from src.utils.datetime_util import DateTimeUtil

class CreateLogModel(BaseModel):
    user: str
    text: str
    type: str
    position: Optional[str] = None
    object_id: str
    created_at: int =  Field(default_factory=DateTimeUtil.current_milli_time)
    action: Optional[str] = None
    duration: Optional[int] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_schema_extra= {
            "example": {
                "user": "user_id",
                "text": "text",
                "type": "string",
                "position": "position",
                "object_id": "object_id",
                "action": "action",
                "duration": 123,
            }
        }
    )