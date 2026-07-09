from typing import Optional, List

from pydantic import BaseModel, ConfigDict, field_validator

from src.models.user.response.user_response_model import UserResponse
from beanie import PydanticObjectId, BackLink, Link

class StatisticUserTask(BaseModel):
    total_point: Optional[int] = None
    total_point_done_tasks: Optional[int] = None
    total_done_tasks: Optional[int] = None
    total_user_task: Optional[int] = None

class SprintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    assignee: Optional[List[UserResponse]] = None
    type: str
    title: str
    des: Optional[str] = None
    status: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    duration: Optional[int] = None
    assigned_id: Optional[list[str]] = None
    parent: Optional[str] = None
    total_tasks: Optional[int] = None
    done_tasks: Optional[int] = None
    order: Optional[str] = None
    statistic_user_task: Optional[dict[str, StatisticUserTask]] = None
    @field_validator(
        'assignee', mode='before'
    )
    @classmethod
    def handle_assignee(cls, v):
        if isinstance(v, Link):
            return None

        if isinstance(v, list) and all(isinstance(item, Link) for item in v):
            return None
        return v

