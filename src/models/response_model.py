from typing import List, Optional, Any

from pydantic import Field, BaseModel, ConfigDict
from src.utils.datetime_util import DateTimeUtil



class ResponseModel(BaseModel):
    data: Optional[Any] = None
    success: Optional[bool] = True
    message: Optional[str] = "Success"
    timestamp: Optional[int] = DateTimeUtil.current_milli_time()
    model_config = ConfigDict(
        populate_by_name = True,
        arbitrary_types_allowed = True,
        json_schema_extra ={
            "example": {
                "data": None,
                "success": True
            }
        }
    )

class ResponsePaginatedModel(BaseModel):
    data: Optional[List[Any]] = None
    success: bool = True
    message: Optional[str] = "Success"
    total: int
    offset: int
    timestamp: Optional[int] = DateTimeUtil.current_milli_time()

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "data": [{}],
                "success": True,
                "total": 1,
                "offset": 1,
                "message": "success"
            }
        }
    )

class ResponseLoginModel(BaseModel):
    access_token: str
    token_type: str = "bearer"

