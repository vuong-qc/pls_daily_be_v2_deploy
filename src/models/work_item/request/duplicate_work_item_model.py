from typing import Optional
from pydantic import BaseModel


class DuplicateWorkItemRequest(BaseModel):
    project_id: str
    sprint_id: Optional[str] = None
    story_id: Optional[str] = None