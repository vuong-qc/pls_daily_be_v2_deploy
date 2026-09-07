from abc import ABC, abstractmethod

from src.enums.result_enum import ResultObjectType
from src.models.result.request.create_result_model import CreateResultModel
from src.models.result.result_document import ResultDocument


class ResultRepository(ABC):
    @abstractmethod
    async def upsert_many_result(self, data: list[CreateResultModel]) -> None: ...

    @abstractmethod
    async def add_close_result(
            self, parent_id: str, type: str, object_ids: list[str], user_id: str,
    ): ...

    @abstractmethod
    async def remove_close_result(
            self, parent_id: str, type: str, object_ids: list[str], user_id: str,
    ): ...

    @abstractmethod
    async def get_results_by_report_id(self, report_id: str) -> list[ResultDocument]: ...

    @abstractmethod
    async def delete_many_result(
            self, report_id: str, object_ids: list[str], object_type: ResultObjectType,
    ) -> None: ...

    @abstractmethod
    async def delete_many_result_by_report_id(self, report_id: str) -> None: ...
