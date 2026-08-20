from pydantic import BaseModel, Field, ConfigDict

from src.utils.datetime_util import DateTimeUtil
from src.enums.tag_status_enum import TagStatusEnum

class CreateTagModel(BaseModel):
    title: str
    des: str
    color: str
    group_id: str
    status: int = Field(default=TagStatusEnum.ENABLE,le=TagStatusEnum.ENABLE.value,gt=TagStatusEnum.DISABLED.value)
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "title",
                "des": "des",
                "color": "color",
                "status": 1,
                "group_id": "group_id",
            }
        }
    )