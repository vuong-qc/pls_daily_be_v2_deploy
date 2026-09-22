from abc import ABC, abstractmethod
from typing import Union, Optional
from src.enums.process_enum import ProcessPeriodType

from src.models.section_result.section_result_document import SectionResultDocument


class SectionResultRepository(ABC):
    @abstractmethod
    async def upsert_result(self, report_id: str, section_item_id: str, value: Union[float, str], created_by: str) -> tuple[SectionResultDocument, bool]: ...

    @abstractmethod
    async def get_result(self, report_id: str, section_item_id: str) -> SectionResultDocument | None: ...

    @abstractmethod
    async def get_results_by_report(self, report_id: str) -> list[SectionResultDocument]: ...

    @abstractmethod
    async def delete_results_by_report(self, report_id: str) -> None: ...

    @abstractmethod
    async def upsert_result_process(self, report_id: str ,section_item_id: str, value: bool, created_by: str, date: int, note: Optional[str] = None)-> tuple[SectionResultDocument, bool]: ...
    @abstractmethod
    async def get_result_process(self, report_id: str, date: int, user_id: str) -> list[SectionResultDocument]: ...
    @abstractmethod
    async def count_bool_results_by_period(
            self,
            item_to_section: dict[str, str],
            start: int,
            end: int,
            period: ProcessPeriodType,
            user_id: str
    ) -> list[dict]: pass
    @abstractmethod
    async def get_result_process_date(self, report_id: str, section_item_id: str, date: int, user_id: str): pass