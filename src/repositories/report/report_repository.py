from abc import ABC, abstractmethod

from src.models.report.report_document import ReportDocument
from src.models.report.request.report_model import FilterReportModel

class ReportRepository(ABC):
    @abstractmethod
    async def create_report(self, data: dict) -> ReportDocument: ...

    @abstractmethod
    async def get_report_by_id(self, report_id: str) -> ReportDocument | None: ...

    @abstractmethod
    async def get_list_reports(self, filters: FilterReportModel, actor_id: str, department_ids: list[str] | None = None) -> list[ReportDocument]: ...

    @abstractmethod
    async def update_report(self, report_id: str, data: dict) -> ReportDocument | None: ...

    @abstractmethod
    async def delete_report(self, report_id: str) -> None: ...
