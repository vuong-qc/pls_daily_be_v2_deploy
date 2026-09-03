from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

from src.models.department.response.department_response_model import DepartmentResponseModel
from src.models.section.response.section_response_model import SectionResponseModel
from src.models.template.response.template_response_model import TemplateResponseModel
from src.models.user.response.user_response_model import UserResponse


class ReportResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: PydanticObjectId
    created_by: Optional[str] = None
    creator_model: Optional[UserResponse] = None
    title: str
    description: Optional[str] = None
    type: str
    template_id: str
    shared_users: list[str] = Field(default_factory=list)
    shared_users_model: list[UserResponse] = Field(default_factory=list)
    shared_departments: list[str] = Field(default_factory=list)
    shared_departments_model: list[DepartmentResponseModel] = Field(default_factory=list)
    status: str
    created_at: int
    updated_at: int
    template: Optional[TemplateResponseModel] = None
    sections: list[SectionResponseModel] = Field(default_factory=list)
