from pydantic import BaseModel
from typing import Optional
class UpdateTemplateModel(BaseModel):
    position: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None