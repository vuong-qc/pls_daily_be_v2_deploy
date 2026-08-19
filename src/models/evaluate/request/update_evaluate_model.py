from pydantic import BaseModel
from typing import Optional
class UpdateEvaluateModel(BaseModel):
    assigned_id: Optional[str] = None
    update_user: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str]= None
    value: Optional[int] = None
    point: Optional[int] = None