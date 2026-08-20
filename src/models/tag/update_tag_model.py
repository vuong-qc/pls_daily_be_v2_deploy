from typing import Optional, Literal
from src.enums.tag_status_enum import TagStatusEnum
from pydantic import BaseModel, ConfigDict

class UpdateTagModel(BaseModel):
    title: Optional[str] = None
    des: Optional[str] = None
    color: Optional[str] = None
    status: Optional[Literal[TagStatusEnum.ENABLE, TagStatusEnum.DISABLED]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "title",
                "des": "des",
                "color": "color",
                "status": 1,
            }
        }
    )
