from src.models.report.request.report_model import FilterReportModel, UpdateReportModel
from src.enums.report_enum import ReportStatusEnum
from src.enums.result_enum import ResultObjectType, ResultStatus, ResultType
from src.enums.template_status_enum import TemplateStatusEnum
from src.exception.report_exception import ReportException, ReportMessage, ReportStatusCode
from src.models.report.request.report_model import CreateReportModel, UpdateReportSharedModel
from src.models.report.response.report_response_model import ReportResponseModel
from src.models.result.request.create_result_model import CreateResultModel
from src.models.template.response.template_response_model import TemplateResponseModel
from src.repositories.department.department_repository import DepartmentRepository
from src.repositories.report.report_repository import ReportRepository
from src.repositories.result.result_repository import ResultRepository
from src.repositories.template.template_repository import TemplateRepository
from src.repositories.user.user_repository import UserRepository
from src.repositories.section_result.section_result_repository import SectionResultRepository
from src.services.section_service import SectionService
from src.utils.datetime_util import DateTimeUtil


class ReportService:
    def __init__(self, report_repository: ReportRepository, template_repository: TemplateRepository,
                 section_service: SectionService, user_repository: UserRepository,
                 department_repository: DepartmentRepository,
                 section_result_repository: SectionResultRepository,
                 result_repository: ResultRepository):
        self.report_repository = report_repository
        self.template_repository = template_repository
        self.section_service = section_service
        self.user_repository = user_repository
        self.department_repository = department_repository
        self.section_result_repository = section_result_repository
        self.result_repository = result_repository

    async def create_report(self, data: CreateReportModel, user_id: str) -> ReportResponseModel:
        template = await self.template_repository.get_template_by_id(data.template_id)
        if not template or template.status != TemplateStatusEnum.PUBLIC:
            raise ReportException(ReportMessage.TEMPLATE_NOT_PUBLIC, ReportStatusCode.TEMPLATE_NOT_PUBLIC)
        report_data = data.model_dump()
        await self._validate_references(report_data)
        report_data.update(created_by=user_id, status=ReportStatusEnum.DRAFT)
        report = await self.report_repository.create_report(report_data)

        await self._upsert_share_results(
            str(report.id), report_data["shared_users"], report_data["shared_departments"]
        )
        return await self.get_report(str(report.id), user_id)

    async def get_report(self, report_id: str, user_id: str) -> ReportResponseModel:
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
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
            values = getattr(data, field)
            update_data[field] = (
                list(dict.fromkeys(values)) if values is not None else list(getattr(report, field))
            )
        await self._validate_references(update_data)
        update_data["updated_at"] = DateTimeUtil.current_milli_time()
        await self.report_repository.update_report(report_id, update_data)
        await self._sync_share_results(
            report_id, update_data["shared_users"], update_data["shared_departments"]
        )
        return await self.get_report(report_id, user_id)

    async def update_report(self, report_id: str, user_id: str, data: UpdateReportModel) -> ReportResponseModel:
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if report.created_by != user_id:
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)

        update_data = data.model_dump(exclude_unset=True)
        new_template_id = data.template_id
        is_template_changed = new_template_id is not None and new_template_id != report.template_id
        if is_template_changed:
            if report.status != ReportStatusEnum.DRAFT:
                raise ReportException(ReportMessage.NOT_EDITABLE, ReportStatusCode.NOT_EDITABLE)
            template = await self.template_repository.get_template_by_id(new_template_id)
            if not template or template.status != TemplateStatusEnum.PUBLIC:
                raise ReportException(ReportMessage.TEMPLATE_NOT_PUBLIC, ReportStatusCode.TEMPLATE_NOT_PUBLIC)
        update_data["updated_at"] = DateTimeUtil.current_milli_time()
        await self.report_repository.update_report(report_id, update_data)
        if is_template_changed and self.section_result_repository:
            await self.section_result_repository.delete_results_by_report(report_id)
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
    async def delete_report(self, report_id: str, user_id: str):
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if report.created_by != user_id:
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)
        if self.result_repository:
            await self.result_repository.delete_many_result_by_report_id(report_id)
        await self.report_repository.delete_report(report_id)

    async def change_status_result_view(self, report_id: str, user_id: str, status: ResultStatus):
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        user = await self.user_repository.get_user_by_id(user_id)
        object_ids = [user_id]
        if user and user.department:
            object_ids.extend(user.department)
        # print("object_ids", object_ids)
        if status == ResultStatus.CLOSED:
            await self.result_repository.add_close_result(report_id, ResultType.REPORT, object_ids, user_id)
        elif status == ResultStatus.DISPLAY:
            await self.result_repository.remove_close_result(report_id, ResultType.REPORT, object_ids, user_id)
        return report

    async def _sync_share_results(self, report_id: str, user_ids: list[str], department_ids: list[str]) -> None:
        if not self.result_repository:
            return
        current_results = await self.result_repository.get_results_by_report_id(report_id)
        current_user_ids = {
            result.object_id for result in current_results
            if result.object_type == ResultObjectType.USER
        }
        current_department_ids = {
            result.object_id for result in current_results
            if result.object_type == ResultObjectType.DEPARTMENT
        }
        target_user_ids = set(user_ids)
        target_department_ids = set(department_ids)

        await self._upsert_share_results(
            report_id,
            list(target_user_ids - current_user_ids),
            list(target_department_ids - current_department_ids),
        )
        await self.result_repository.delete_many_result(
            report_id, list(current_user_ids - target_user_ids), ResultObjectType.USER
        )
        await self.result_repository.delete_many_result(
            report_id, list(current_department_ids - target_department_ids), ResultObjectType.DEPARTMENT
        )

    async def _upsert_share_results(self, report_id: str, user_ids: list[str], department_ids: list[str]) -> None:
        if not self.result_repository:
            return
        results = [
            CreateResultModel(
                parent_id=report_id,
                type=ResultType.REPORT,
                object_id=object_id,
                object_type=object_type,
                # status=ResultStatus.DISPLAY,
            )
            for object_type, object_ids in (
                (ResultObjectType.USER, user_ids),
                (ResultObjectType.DEPARTMENT, department_ids),
            )
            for object_id in object_ids
        ]
        await self.result_repository.upsert_many_result(results)

    async def _validate_references(self, data: dict) -> None:
        user_ids = set(data.get("shared_users", []))
        for user_id in user_ids:
            if not await self.user_repository.get_user_by_id(user_id):
                raise ReportException(ReportMessage.USER_NOT_FOUND, ReportStatusCode.USER_NOT_FOUND)
        department_ids = set(data.get("shared_departments", []))
        for department_id in department_ids:
            if not await self.department_repository.get_department_by_id(department_id):
                raise ReportException(ReportMessage.DEPARTMENT_NOT_FOUND, ReportStatusCode.DEPARTMENT_NOT_FOUND)
