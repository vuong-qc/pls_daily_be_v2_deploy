from pydantic import BaseModel
from typing import Optional

class UpdateChatbotTokenModel(BaseModel):
    type: Optional[str]
    token: Optional[str]
    key: Optional[str]
    position: Optional[str]
    space_id: Optional[str]