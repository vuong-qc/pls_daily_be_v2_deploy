from pydantic import BaseModel, field_validator
from typing import List, Optional
from src.enums.sprint_status_enum import SprintStatusEnum

class UpdateSprintModel(BaseModel):
    duration: Optional[int] = None
    start: Optional[int] = None
    end: Optional[int] = None
    title: Optional[str] = None
    des: Optional[str] = None
    status: Optional[SprintStatusEnum] = None
    assigned_id: Optional[list[str]] = None

    order_type: Optional[str] = None
    next_order: Optional[str] = None
    prev_order: Optional[str] = None