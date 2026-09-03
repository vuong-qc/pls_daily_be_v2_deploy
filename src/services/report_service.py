from src.models.report.request.report_model import FilterReportModel, UpdateReportModel
from src.enums.report_enum import ReportStatusEnum
from src.enums.template_status_enum import TemplateStatusEnum
from src.exception.report_exception import ReportException, ReportMessage, ReportStatusCode
from src.models.report.request.report_model import CreateReportModel, UpdateReportSharedModel
from src.models.report.response.report_response_model import ReportResponseModel
from src.models.template.response.template_response_model import TemplateResponseModel
from src.repositories.department.department_repository import DepartmentRepository
from src.repositories.report.report_repository import ReportRepository
from src.repositories.template.template_repository import TemplateRepository
from src.repositories.user.user_repository import UserRepository
from src.services.section_service import SectionService
from src.utils.datetime_util import DateTimeUtil


class ReportService:
    shared_visible_statuses = {
        ReportStatusEnum.SUBMITTED,
        ReportStatusEnum.DISPLAY,
        ReportStatusEnum.CLOSED,
    }

    def __init__(self, report_repository: ReportRepository, template_repository: TemplateRepository,
                 section_service: SectionService, user_repository: UserRepository,
                 department_repository: DepartmentRepository):
        self.report_repository = report_repository
        self.template_repository = template_repository
        self.section_service = section_service
        self.user_repository = user_repository
        self.department_repository = department_repository

    async def create_report(self, data: CreateReportModel, user_id: str) -> ReportResponseModel:
        template = await self.template_repository.get_template_by_id(data.template_id)
        if not template or template.status != TemplateStatusEnum.PUBLIC:
            raise ReportException(ReportMessage.TEMPLATE_NOT_PUBLIC, ReportStatusCode.TEMPLATE_NOT_PUBLIC)
        report_data = data.model_dump()
        await self._validate_references(report_data)
        report_data.update(created_by=user_id, status=ReportStatusEnum.DRAFT)
        report = await self.report_repository.create_report(report_data)
        return await self.get_report(str(report.id), user_id)

    async def get_report(self, report_id: str, user_id: str) -> ReportResponseModel:
        report = await self._get_report_with_access(report_id, user_id)
        template = await self.template_repository.get_template_by_id(report.template_id, ignore_deleted=True)
        sections = await self.section_service.get_section_tree(report.template_id)
        response = ReportResponseModel.model_validate(report)
        return response.model_copy(update={
            "template": TemplateResponseModel.model_validate(template) if template else None,
            "sections": sections,
        })

    async def get_list_reports(self, filters: FilterReportModel, user_id: str) -> list[ReportResponseModel]:
        user = await self.user_repository.get_user_by_id(user_id)
        reports = await self.report_repository.get_list_reports(filters, user_id, user.department or [] if user else [])
        return [ReportResponseModel.model_validate(report) for report in reports]

    async def update_shared(self, report_id: str, data: UpdateReportSharedModel, user_id: str) -> ReportResponseModel:
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if report.created_by != user_id:
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)
        update_data = {}
        for field in ("shared_users", "shared_departments"):
            additions = getattr(data, field)
            if additions is not None:
                update_data[field] = list(dict.fromkeys(getattr(report, field) + additions))
        await self._validate_references(update_data)
        update_data["updated_at"] = DateTimeUtil.current_milli_time()
        await self.report_repository.update_report(report_id, update_data)
        return await self.get_report(report_id, user_id)

    async def update_report(self, report_id: str, user_id: str, data: UpdateReportModel) -> ReportResponseModel:
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if report.created_by != user_id:
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = DateTimeUtil.current_milli_time()
        await self.report_repository.update_report(report_id, update_data)
        return await self.get_report(report_id, user_id)

    async def change_status(self, report_id: str, target_status: ReportStatusEnum,
                            user_id: str) -> ReportResponseModel:
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if report.created_by != user_id:
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)
        await self.report_repository.update_report(report_id, {
            "status": target_status,
            "updated_at": DateTimeUtil.current_milli_time(),
        })
        return await self.get_report(report_id, user_id)

    async def _get_report_with_access(self, report_id: str, user_id: str):
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if user_id == report.created_by:
            return report
        is_shared_user = user_id in report.shared_users
        user = await self.user_repository.get_user_by_id(user_id)
        user_groups = set(user.department or []) if user else set()
        is_shared_department = bool(user_groups.intersection(report.shared_departments))
        if (not is_shared_user and not is_shared_department) or report.status not in self.shared_visible_statuses:
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)
        return report

    async def _validate_references(self, data: dict) -> None:
        user_ids = set(data.get("shared_users", []))
        for user_id in user_ids:
            if not await self.user_repository.get_user_by_id(user_id):
                raise ReportException(ReportMessage.USER_NOT_FOUND, ReportStatusCode.USER_NOT_FOUND)
        department_ids = set(data.get("shared_departments", []))
        for department_id in department_ids:
            if not await self.department_repository.get_department_by_id(department_id):
                raise ReportException(ReportMessage.DEPARTMENT_NOT_FOUND, ReportStatusCode.DEPARTMENT_NOT_FOUND)
