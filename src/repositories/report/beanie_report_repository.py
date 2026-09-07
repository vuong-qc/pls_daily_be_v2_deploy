import re

from beanie import PydanticObjectId
from beanie.operators import In, Set, And, GTE, LTE, RegEx, Or, Eq

from src.enums.result_enum import ResultStatus
from src.enums.report_enum import ReportStatusEnum
from src.enums.result_enum import ResultObjectType, ResultType
from src.models.department.department_document import DepartmentDocument
from src.models.report.report_document import ReportDocument
from src.models.report.request.report_model import FilterReportModel
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

    async def get_list_reports(
            self, filters: FilterReportModel, actor_id: str,
            department_ids: list[str] | None = None,
    ) -> list[ReportDocument]:
        report_match: dict = {"deleted_at": None}
        if filters.status:
            if ReportStatusEnum.DRAFT in filters.status:
                report_match.update(
                    Or(
                        And(
                            Eq(ReportDocument.created_by, actor_id),
                            Eq(ReportDocument.status, ReportStatusEnum.DRAFT.value),
                        ),
                        Eq(ReportDocument.status, [status.value for status in filters.status if status.value != ReportStatusEnum.DRAFT]),
                    )
                )
            else:
                report_match.update(In(ReportDocument.status, [status.value for status in filters.status]))
        if filters.created_by:
            report_match.update(In(ReportDocument.created_by, filters.created_by))
            # report_match["created_by"] = {"$in": filters.created_by}
        if filters.start_date and filters.end_date:
            report_match.update(
                And(
                    GTE(ReportDocument.created_at, filters.start_date),
                    LTE(ReportDocument.created_at, filters.end_date),
                )
            )
        elif filters.start_date:
            report_match.update(
                GTE(ReportDocument.created_at, filters.start_date)
            )
        elif filters.end_date:
            report_match.update(
                LTE(ReportDocument.created_at, filters.end_date)
            )
        if filters.search:

            report_match.update(
                RegEx(ReportDocument.title,re.escape(filters.search.strip()), "i")
            )

        object_filters = [{
            "$and": [
                {"$eq": ["$object_type", ResultObjectType.USER.value]},
                {"$eq": ["$object_id", actor_id]},
            ]
        }]
        if department_ids:
            object_filters.append({
                "$and": [
                    {"$eq": ["$object_type", ResultObjectType.DEPARTMENT]},
                    {"$in": ["$object_id", department_ids]},
                ]
            })

        pipeline = [
            {"$match": report_match},
        ]
        result_match = [
            {"$eq": ["$parent_id", "$$report_id"]},
            {"$eq": ["$type", ResultType.REPORT]},
            {"$eq": ["$deleted_at", None]},
            {"$or": object_filters},
        ]
        if filters.result_status is not None:
            # result_match.append({"$eq": ["$status", filters.result_status.value]})
            closed_by_expr = {"$ifNull": ["$closed_by", []]}
            if filters.result_status == ResultStatus.CLOSED:
                result_match.append(
                    {"$in": [actor_id, closed_by_expr]}
                )
            else:
                result_match.append(
                    {"$not": [{"$in": [actor_id, closed_by_expr]}]}
                )
            pipeline.extend(
                [
                    {
                        "$lookup": {
                            "from": "results",
                            "let": {"report_id": {"$toString": "$_id"}},
                            "pipeline": [{"$match": {"$expr": {"$and": result_match}}}],
                            "as": "access_results",
                        }
                    },
                    {
                        "$match": {
                            "$or": [
                                {"access_results.0": {"$exists": True}},
                            ]
                        }
                    },
                ]
            )

        pipeline.extend(
            [

            {"$sort": {"created_at": -1}},
            {"$project": {"_id": 1}},
        ]
        )
        rows = await ReportDocument.aggregate(pipeline).to_list()
        report_ids = [row["_id"] for row in rows]
        if not report_ids:
            return []
        return await ReportDocument.find(
            In(ReportDocument.id, report_ids),
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
