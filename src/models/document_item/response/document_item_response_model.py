from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from typing import Optional

from src.models.sprint.response.sprint_response_model import SprintResponse
from src.models.task.response.task_response_model import TaskResponse
from src.models.user.response.user_response_model import UserResponse
from src.models.document_result.response.document_result_response import DocumentResultResponse


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    group_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    type: str
    date_time: int
    object_id: Optional[str] = None
    result: Optional[DocumentResultResponse] = None
    created_by: Optional[str] = None
    is_archived: Optional[bool] = False
    is_checked: Optional[bool] = False
    is_urgent: Optional[bool] = False
    priority: Optional[str] = None
    notes: Optional[str] = None
    assignee: Optional[list[str]] = None
    sprint: Optional[str] = None
    task: Optional[str] = None
    precondition: Optional[str] = None
    step_implement: Optional[str] = None
    role: Optional[str] = None
    data_test: Optional[str] = None
    expect_result: Optional[str] = None
    final_result: Optional[str] = None
    handler: Optional[str] = None
    scenario: Optional[str] = None
    feature: Optional[str] = None
    assignee_model: Optional[list[UserResponse]] = None
    handler_model: Optional[UserResponse] = None
    task_model: Optional[TaskResponse] = None
    sprint_model: Optional[SprintResponse] = None
    deadline: Optional[int] = None
