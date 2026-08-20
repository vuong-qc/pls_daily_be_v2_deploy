from typing import Optional

from pydantic import BaseModel

class UpdateCommentModel(BaseModel):
    content: Optional[str] = None