from pydantic import BaseModel
from typing import Optional

class CreateDepartmentModel(BaseModel):
    name: str
    des: str
    icon: Optional[str] = None
    chatbot_token_id: Optional[str] = None
