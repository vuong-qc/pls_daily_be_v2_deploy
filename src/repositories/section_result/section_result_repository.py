from abc import ABC, abstractmethod
from typing import Union

from src.models.section_result.section_result_document import SectionResultDocument


class SectionResultRepository(ABC):
    @abstractmethod
    async def upsert_result(self, report_id: str, section_item_id: str, value: Union[float, str], created_by: str) -> tuple[SectionResultDocument, bool]: ...

    @abstractmethod
    async def get_result(self, report_id: str, section_item_id: str) -> SectionResultDocument | None: ...

    @abstractmethod
    async def get_results_by_report(self, report_id: str) -> list[SectionResultDocument]: ...
