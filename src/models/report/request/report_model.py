from typing import Optional

from pydantic import BaseModel, Field

from src.enums.report_enum import ReportStatusEnum, ReportTypeEnum


class CreateReportModel(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = ReportTypeEnum.PERSONAL
    template_id: str
    shared_users: list[str] = Field(default_factory=list)
    shared_departments: list[str] = Field(default_factory=list)


class UpdateReportSharedModel(BaseModel):
    shared_users: Optional[list[str]] = None
    shared_departments: Optional[list[str]] = None


class UpdateReportStatusModel(BaseModel):
    status: ReportStatusEnum

class FilterReportModel(BaseModel):
    search: Optional[str] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    status: Optional[list[ReportStatusEnum]] = None
    created_by: Optional[list[str]] = None


class UpdateReportModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
