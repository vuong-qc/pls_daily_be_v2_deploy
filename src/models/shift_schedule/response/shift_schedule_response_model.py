from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId

class ShiftScheduleResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    user_id: str
    status: str
    start_time: int
    end_time: int
    created_at: int
    updated_at: int
    weekday: int