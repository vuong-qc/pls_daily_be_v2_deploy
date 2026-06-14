from pydantic import BaseModel
from typing import Optional

class FilterOrderModel(BaseModel):
    type: Optional[str] = None
    parent_id: Optional[str] = None
    owner_id: Optional[str] = None
    object_id: Optional[str] = None
    offset: Optional[int] = None
    limit: Optional[int] = None