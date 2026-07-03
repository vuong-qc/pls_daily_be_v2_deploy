
from typing import List, Optional
from src.models.user.response.user_response_model import UserResponse
from src.models.project.response.project_response_base_model import ProjectInfo

class ProjectResponse(ProjectInfo):
    handler_id: Optional[List[str]] = None
    handler: Optional[List[UserResponse]] = None
    owner: Optional[UserResponse] = None
    total_children: Optional[int] = None
    processing_children: Optional[int] = None

