from typing import Optional

from pydantic import BaseModel

class CreateOrderModel(BaseModel):
    type: str
    object_id: str
    owner_id: str
    parent_id: Optional[str] = None
    order: Optional[str] = None