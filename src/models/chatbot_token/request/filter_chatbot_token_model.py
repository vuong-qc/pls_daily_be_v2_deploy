from pydantic import BaseModel, Field
from typing import Optional

class FilterChatbotTokenModel(BaseModel):
    type: Optional[list[str]] = None
    position: Optional[list[str]] = None
    offset: int = 0
    limit: int = Field(10, le=100)