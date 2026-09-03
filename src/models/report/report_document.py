from typing import Annotated, Optional

import pymongo
from beanie import DocumentWithSoftDelete, Indexed, Link
from pydantic import Field

from src.enums.report_enum import ReportStatusEnum, ReportTypeEnum
from src.models.department.department_document import DepartmentDocument
from src.models.user.user_document import UserDocument
from src.utils.datetime_util import DateTimeUtil


class ReportDocument(DocumentWithSoftDelete):
    created_by: Optional[str] = None
    creator_model: Optional[Link[UserDocument]] = None
    title: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    description: Optional[str] = None
    type: str = ReportTypeEnum.PERSONAL
    template_id: Indexed(str)
    shared_users: list[str] = Field(default_factory=list)
    shared_users_model: list[Link[UserDocument]] = Field(default_factory=list)
    shared_departments: list[str] = Field(default_factory=list)
    shared_departments_model: list[Link[DepartmentDocument]] = Field(default_factory=list)
    status: str = ReportStatusEnum.DRAFT
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    class Settings:
        name = "reports"
