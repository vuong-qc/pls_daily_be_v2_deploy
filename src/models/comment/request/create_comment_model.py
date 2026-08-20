from typing import Optional

from pydantic import BaseModel

class CreateCommentModel(BaseModel):
    object_id: str
    creator_id: str
    parent_id: Optional[str] = None
    content: str