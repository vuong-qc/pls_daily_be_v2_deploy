from pydantic import BaseModel
from typing import Optional
class UpdateTemplateModel(BaseModel):
    prev_order: Optional[str] = None
    next_order: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
