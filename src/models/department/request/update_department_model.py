from typing import Optional
from pydantic import BaseModel
class UpdateDepartmentModel(BaseModel):
    name: Optional[str] = None
    des: Optional[str] = None
    icon: Optional[str] = None
    chatbot_token_id: Optional[str] = None

