from pydantic import BaseModel

class CreateChatbotToken(BaseModel):
    type: str
    token: str
    position: str
    space_id: str
    key: str