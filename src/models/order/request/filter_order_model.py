from pydantic import BaseModel
from typing import Optional

class FilterOrderModel(BaseModel):
    type: Optional[str]
    object_id: Optional[str]
    owner_id: Optional[str]