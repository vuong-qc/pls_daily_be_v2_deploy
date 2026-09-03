from beanie import PydanticObjectId
from beanie.operators import And, In, Or, Set, GTE, LTE, RegEx
import re
from src.models.report.request.report_model import FilterReportModel
from src.enums.report_enum import ReportStatusEnum
from src.models.department.department_document import DepartmentDocument
from src.models.report.report_document import ReportDocument
from src.models.user.user_document import UserDocument
from src.repositories.report.report_repository import ReportRepository


class BeanieReportRepository(ReportRepository):
    async def create_report(self, data: dict) -> ReportDocument:
        report = ReportDocument(**data)
        self._add_link_docs(data, report)
        await report.insert()
        return await ReportDocument.get(report.id, fetch_links=True)

    async def get_report_by_id(self, report_id: str) -> ReportDocument | None:
        if not PydanticObjectId.is_valid(report_id):
            return None
        return await ReportDocument.get(report_id, fetch_links=True)

    async def get_list_reports(self, filters: FilterReportModel, actor_id: str, department_ids: list[str] | None = None,) -> list[ReportDocument]:
        filter_dump = filters.model_dump(exclude_unset=True)
        keyword = filter_dump.pop("search", None)
        start_date = filter_dump.pop("start_date", None)
        end_date = filter_dump.pop("end_date", None)

        if filters.created_by:
            filter_dump.update(
                In(ReportDocument.created_by, filters.created_by)
            )
            if filters.status:
                filter_dump.update(In(ReportDocument.status, [status for status in filters.status if status != ReportStatusEnum.DRAFT]))
                filters.status = None
        else:
            filter_dump.update(
                Or(
                ReportDocument.created_by == actor_id,
                And(
                    Or(
                        In(ReportDocument.shared_users, [actor_id]),
                        In(ReportDocument.shared_departments, department_ids or []),
                    ),
                    In(ReportDocument.status, [
                        ReportStatusEnum.SUBMITTED,
                        ReportStatusEnum.DISPLAY,
                        ReportStatusEnum.CLOSED,
                    ] if not filters.status else [status for status in filters.status if status != ReportStatusEnum.DRAFT]),
                ),
                ),
            )
            filters.status = None
        if filters.status:
            filter_dump.update(
                In(ReportDocument.status, filters.status)
            )

        if filters.start_date and filters.end_date:
            filter_dump.update(
                And(
                    GTE(ReportDocument.created_at, start_date),
                    LTE(ReportDocument.created_at, end_date),
                )
            )
        if keyword:
            normal_key = re.escape(keyword.strip())
            filter_dump.update(
                RegEx(
                    ReportDocument.title, normal_key, "i"
                )
            )

        return await ReportDocument.find(
            filter_dump,
            fetch_links=True,
        ).sort("-created_at").to_list()

    async def update_report(self, report_id: str, data: dict) -> ReportDocument | None:
        report = await self.get_report_by_id(report_id)
        if report:
            self._add_link_docs(data, report)
            await report.save()
            await report.update(Set(data))
            return await ReportDocument.get(report.id, fetch_links=True)
        return None

    async def delete_report(self, report_id: str) -> None:
        report = await self.get_report_by_id(report_id)
        if report:
            await report.delete()

    def _add_link_docs(self, data: dict, report: ReportDocument) -> None:
        if "created_by" in data:
            report.creator_model = self._build_user_link(data.get("created_by"))
        if "shared_users" in data:
            report.shared_users_model = self._build_user_links(data.get("shared_users", []))
        if "shared_departments" in data:
            report.shared_departments_model = [
                DepartmentDocument.model_construct(id=PydanticObjectId(department_id))
                for department_id in data.get("shared_departments", [])
                if PydanticObjectId.is_valid(department_id)
            ]

    def _build_user_link(self, user_id: str | None):
        if user_id and PydanticObjectId.is_valid(user_id):
            return UserDocument.model_construct(id=PydanticObjectId(user_id))
        return None

    def _build_user_links(self, user_ids: list[str]):
        return [link for user_id in user_ids if (link := self._build_user_link(user_id))]
