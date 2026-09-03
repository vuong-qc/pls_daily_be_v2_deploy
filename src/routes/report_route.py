from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from src.models.report.request.report_model import FilterReportModel, UpdateReportModel
from src.models.report.request.report_model import CreateReportModel, UpdateReportSharedModel, UpdateReportStatusModel
from src.models.response_model import ResponseModel
from src.models.section_result.request.section_result_model import UpsertSectionResultModel
from src.repositories.department.beanie_department_repository import BeanieDepartmentRepository
from src.repositories.report.beanie_report_repository import BeanieReportRepository
from src.repositories.section.beanie_section_repository import BeanieSectionRepository
from src.repositories.section_result.beanie_section_result_repository import BeanieSectionResultRepository
from src.repositories.template.beanie_template_repository import BeanieTemplateRepository
from src.repositories.user.beanie_user_repository import BeanieUserRepository
from src.services.report_service import ReportService
from src.services.section_result_service import SectionResultService
from src.services.section_service import SectionService
from src.utils.proxy_util import get_current_user_by_token

router = APIRouter(tags=["report"])


def get_report_service():
    template_repository = BeanieTemplateRepository()
    section_service = SectionService(BeanieSectionRepository(), template_repository)
    return ReportService(BeanieReportRepository(), template_repository, section_service,
                         BeanieUserRepository(), BeanieDepartmentRepository())


def get_section_result_service():
    return SectionResultService(BeanieSectionResultRepository(), BeanieSectionRepository(),
                                BeanieReportRepository(), BeanieUserRepository())


@router.get("/get-reports", response_model=ResponseModel)
async def get_reports(
        query: Annotated[FilterReportModel, Query()],
        service: ReportService = Depends(get_report_service),
        user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.get_list_reports(query, user_data["sub"]))

@router.post("/create-report", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_report(data: CreateReportModel, service: ReportService = Depends(get_report_service),
                        user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.create_report(data, user_data["sub"]))


@router.patch("/share-report/{report_id}", response_model=ResponseModel)
async def update_report_shared(report_id: str, data: UpdateReportSharedModel,
                               service: ReportService = Depends(get_report_service),
                               user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.update_shared(report_id, data, user_data["sub"]))


@router.patch("/update-report-status/{report_id}", response_model=ResponseModel)
async def update_report_status(report_id: str, data: UpdateReportStatusModel,
                               service: ReportService = Depends(get_report_service),
                               user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.change_status(report_id, data.status, user_data["sub"]))

@router.patch("/update-report/{report_id}", response_model=ResponseModel)
async def update_report_status(report_id: str, data: UpdateReportModel,
                               service: ReportService = Depends(get_report_service),
                               user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.update_report(report_id, user_data["sub"], data))


@router.put("/update-report-section/{report_id}/sections/{section_item_id}/value", response_model=ResponseModel)
async def upsert_section_result(report_id: str, section_item_id: str, data: UpsertSectionResultModel,
                                service: SectionResultService = Depends(get_section_result_service),
                                user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.upsert_result(report_id, section_item_id, data.value, user_data["sub"]))


@router.get("/get-report/{report_id}/results", response_model=ResponseModel)
async def get_section_results(report_id: str, service: SectionResultService = Depends(get_section_result_service),
                              user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.get_results(report_id, user_data["sub"]))
@router.get("/get-report/{report_id}", response_model=ResponseModel)
async def get_report(report_id: str, service: ReportService = Depends(get_report_service),
                     user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.get_report(report_id, user_data["sub"]))

