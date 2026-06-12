from pydantic import BaseModel, ConfigDict

class ChatbotTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    token: str
    position: str
    space_id: str
    key: str