from typing import Optional

from pydantic import BaseModel, Field

class FilterDocumentResult(BaseModel):
    owner_id: Optional[list[str]] = None
    parent_id: Optional[list[str]] = None
    is_closed: Optional[bool] = False
    evaluate: Optional[str] = None
    limit: int = Field(10)
    offset: int =0