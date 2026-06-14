from pydantic import BaseModel
from typing import Optional

class UpdateOrderModel(BaseModel):
    type: Optional[str] = None
    parent_id: Optional[str] = None
