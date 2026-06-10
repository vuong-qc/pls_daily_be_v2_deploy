from pydantic import BaseModel, Field
from typing import Optional

from src.enums.sprint_status_enum import SprintStatusEnum


class FilterSprintModel(BaseModel):
    status: Optional[SprintStatusEnum] = None
    project_id: Optional[list[str]] = None
    limit: int = Field(10,le=100)
    offset: int = 0
