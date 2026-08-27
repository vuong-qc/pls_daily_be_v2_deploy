from pydantic import BaseModel
from typing import Optional
class CreateTemplateModel(BaseModel):
    created_by: Optional[str] = None
    position: Optional[str] = None
    title: str
    description: Optional[str] = None
    group: str