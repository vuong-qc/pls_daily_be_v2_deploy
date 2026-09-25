from numbers import Real
from typing import Union, Optional

from src.exception.template_exception import TemplateException, TemplateMessage, TemplateStatusCode
from src.enums.report_enum import ReportStatusEnum
from src.enums.section_enum import SectionTypeEnum, SectionValueTypeEnum
from src.exception.report_exception import ReportException, ReportMessage, ReportStatusCode
from src.exception.section_result_exception import SectionResultException, SectionResultMessage, SectionResultStatusCode
from src.models.section_result.response.section_result_response_model import SectionResultResponseModel
from src.repositories.report.report_repository import ReportRepository
from src.repositories.section.section_repository import SectionRepository
from src.repositories.section_result.section_result_repository import SectionResultRepository
from src.repositories.user.user_repository import UserRepository
from src.repositories.template.template_repository import TemplateRepository
from src.models.section_result.request.section_result_model import FilterResultModel


class SectionResultService:
    def __init__(self, result_repository: SectionResultRepository, section_repository: SectionRepository,
                 report_repository: ReportRepository, template_repository: TemplateRepository,
                 user_repository: UserRepository | None = None):
        self.result_repository = result_repository
        self.section_repository = section_repository
        self.report_repository = report_repository
        self.user_repository = user_repository
        self.template_repository = template_repository

    async def upsert_result(self, report_id: str, section_item_id: str,
                            value: Union[float, str, bool], user_id: str) -> SectionResultResponseModel:
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if report.created_by != user_id:
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)
        # if report.status != ReportStatusEnum.DRAFT:
        #     raise ReportException(ReportMessage.NOT_EDITABLE, ReportStatusCode.NOT_EDITABLE)
        item = await self.section_repository.get_section_by_id(section_item_id)
        if not item or item.type != SectionTypeEnum.ITEM:
            raise SectionResultException(SectionResultMessage.ITEM_NOT_FOUND, SectionResultStatusCode.ITEM_NOT_FOUND)
        parent = await self.section_repository.get_section_by_id(item.parent_id)
        if not parent or parent.parent_id != report.template_id:
            raise SectionResultException(SectionResultMessage.ITEM_NOT_BELONG, SectionResultStatusCode.ITEM_NOT_BELONG)
        valid_value = self._validate_value(item.value_type, value)
        result, _ = await self.result_repository.upsert_result(
            report_id, section_item_id, valid_value, user_id
        )
        return SectionResultResponseModel.model_validate(result)

    async def get_results(self, report_id: str, user_id: str) -> list[SectionResultResponseModel]:
        report = await self.report_repository.get_report_by_id(report_id)
        if not report:
            raise ReportException(ReportMessage.NOT_FOUND, ReportStatusCode.NOT_FOUND)
        if not await self._has_access(report, user_id):
            raise ReportException(ReportMessage.FORBIDDEN, ReportStatusCode.FORBIDDEN)
        results = await self.result_repository.get_results_by_report(report_id)
        return [SectionResultResponseModel.model_validate(result) for result in results]

    async def upsert_result_process(self, template_id: str, section_item_id: str,
                            value: bool, user_id: str, date: int, note: Optional[str]=None) -> SectionResultResponseModel:
        template = await self.template_repository.get_template_by_id(template_id)
        if not template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)
        # if template.created_by != user_id:
        #     raise TemplateException(TemplateMessage.NOT_OWNER, TemplateStatusCode.NOT_OWNER)
        # if report.status != ReportStatusEnum.DRAFT:
        #     raise ReportException(ReportMessage.NOT_EDITABLE, ReportStatusCode.NOT_EDITABLE)
        item = await self.section_repository.get_section_by_id(section_item_id)
        if not item or item.type != SectionTypeEnum.ITEM:
            raise SectionResultException(SectionResultMessage.ITEM_NOT_FOUND, SectionResultStatusCode.ITEM_NOT_FOUND)
        parent = await self.section_repository.get_section_by_id(item.parent_id)
        if not parent or parent.parent_id != template_id:
            raise SectionResultException(SectionResultMessage.ITEM_NOT_BELONG, SectionResultStatusCode.ITEM_NOT_BELONG)
        valid_value = self._validate_value(item.value_type, value)
        result, _ = await self.result_repository.upsert_result_process(
            template_id, section_item_id, valid_value, user_id, date, note
        )
        return SectionResultResponseModel.model_validate(result)

    async def get_process_results(self, template_id: str, user_id: str, date: int) -> list[SectionResultResponseModel]:
        template = await self.template_repository.get_template_by_id(template_id)
        if not template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)
        results = await self.result_repository.get_result_process(template_id, date, user_id)
        return [SectionResultResponseModel.model_validate(result) for result in results]


    async def get_process_result_by_range(self, filters: FilterResultModel):
        # get all section of template
        # get all item of section
        # query group date , section contain item with count result is check
        template = await self.template_repository.get_template_by_id(filters.template_id)
        if not template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)
        if not template.type:
            raise TemplateException(TemplateMessage.PROCESS_TYPE_NOT_MATCH, TemplateStatusCode.PROCESS_TYPE_NOT_MATCH)
        sections = await self.section_repository.get_section_ids_by_parent_id(filters.template_id, SectionTypeEnum.SECTION)
        item_to_section = await self.section_repository.get_parent_by_section_ids(sections)
        count_check_result = await self.result_repository.count_bool_results_by_period(
            item_to_section, filters.start, filters.end, template.type, filters.user_id
        )
        print("count_check_result", count_check_result)
        return count_check_result
    async def _has_access(self, report, user_id: str) -> bool:
        if user_id == report.created_by:
            return True
        if report.status != ReportStatusEnum.SUBMITTED:
            return False
        if user_id in report.shared_users:
            return True
        if not self.user_repository or not report.shared_departments:
            return False
        user = await self.user_repository.get_user_by_id(user_id)
        return bool(user and set(user.department or []).intersection(report.shared_departments))

    def _validate_value(self, value_type: str, value: Union[float, str,bool]) -> Union[float, str,bool]:
        is_number = isinstance(value, Real) and not isinstance(value, bool)
        if value_type == SectionValueTypeEnum.NUMBER and is_number:
            return float(value)
        if value_type == SectionValueTypeEnum.TEXT and isinstance(value, str):
            return value
        if value_type == SectionValueTypeEnum.PROGRESS and is_number and 0 <= value <= 100:
            return float(value)
        if value_type == SectionValueTypeEnum.CHECK and isinstance(value, bool):
            return value
        if value_type == SectionValueTypeEnum.EVALUATE and isinstance(value, str):
            return value

        raise SectionResultException(SectionResultMessage.INVALID_VALUE, SectionResultStatusCode.INVALID_VALUE)
