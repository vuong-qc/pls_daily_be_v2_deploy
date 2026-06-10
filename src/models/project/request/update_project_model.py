from pydantic import BaseModel
from typing import Optional, List
from src.enums.project_status_enum import ProjectStatusEnum

class UpdateProjectModel(BaseModel):
    title: Optional[str] = None
    des: Optional[str] = None
    handler_id: Optional[List[str]] = None
    status: Optional[ProjectStatusEnum] = None