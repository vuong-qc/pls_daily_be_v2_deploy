from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId

class ChatbotTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    type: str
    token: str
    position: str
    space_id: str
    key: str