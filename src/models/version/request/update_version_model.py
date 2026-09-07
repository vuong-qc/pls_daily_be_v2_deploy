from pydantic import BaseModel
from typing import Optional

class UpdateVersionModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    files: Optional[list[str]] = None
    version: Optional[str] = None