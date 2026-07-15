from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from typing import Optional

class DepartmentResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    name: str
    des: str
    icon: Optional[str] = None
    chatbot_token_id: Optional[str] = None