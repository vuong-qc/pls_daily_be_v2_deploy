from pydantic import BaseModel, Field
from typing import Optional

class FilterCommentModel(BaseModel):
    object_id: Optional[str] = None
    parent_id: Optional[str] = None
    offset: int = 0
    limit: int = Field(10, le=100)
