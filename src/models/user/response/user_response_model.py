from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId
from typing import List, Optional, Any
from datetime import datetime
from src.models.project.response.project_response_base_model import ProjectInfo


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    dob: Optional[datetime] = None
    avt: str = ""
    email: str
    name: str
    phone: Optional[str] = None
    roles: List[int]
    require_pass_update: bool = True
    status: int = 0
    gender: int
    traineeStatus: int
    address: Optional[str] = None
    # user_code: int = Indexed(unique=True)
    created_at: int
    updated_at: int
    department: Optional[str] = None

class UserDetails(UserResponse):
    projects: Optional[list[ProjectInfo]] = []
