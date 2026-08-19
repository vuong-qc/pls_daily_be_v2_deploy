from pydantic import BaseModel
from typing import Optional
class CreateEvaluateModel(BaseModel):
    creator_id: str
    assigned_id: str
    update_user: Optional[str] = None
    title: str
    description: Optional[str]= None
    value: Optional[int] = None
    point: Optional[int] = None