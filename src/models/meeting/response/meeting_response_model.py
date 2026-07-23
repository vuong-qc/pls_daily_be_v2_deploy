from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId

class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId