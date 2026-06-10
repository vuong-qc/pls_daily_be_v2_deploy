from pydantic import BaseModel
from typing import Optional

class UpdateDocumentItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    files: Optional[list[str]] = None
    object_id: Optional[str] = None
