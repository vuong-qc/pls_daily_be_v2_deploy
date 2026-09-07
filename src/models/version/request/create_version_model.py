from pydantic import BaseModel
from typing import Optional

class CreateVersionModel(BaseModel):
    type: str
    object_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    version: Optional[str] = None