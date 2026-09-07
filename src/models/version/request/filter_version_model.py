from typing import Optional

from pydantic import BaseModel
class FilterVersionModel(BaseModel):
    type: Optional[list[str]] = None
    object_id: Optional[list[str]] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0