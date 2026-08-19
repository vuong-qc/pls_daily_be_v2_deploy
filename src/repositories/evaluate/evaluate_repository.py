from abc import abstractmethod, ABC
from src.models.evaluate.evaluate_document import EvaluateDocument
from src.models.evaluate.request.filter_evaluate_model import FilterEvaluateModel


class EvaluateRepository(ABC):
    @abstractmethod
    async def create_evaluate(self, data: dict) -> EvaluateDocument:
        pass
    @abstractmethod
    async def update_evaluate(self, evaluate_id: str, data: dict) -> EvaluateDocument | None:
        pass
    @abstractmethod
    async def delete_evaluate(self, evaluate_id: str) -> None:
        pass
    @abstractmethod
    async def get_evaluate_by_id(self, evaluate_id: str) -> EvaluateDocument | None:
        pass
    @abstractmethod
    async def get_list_evaluate(self, filter_evaluate_model: FilterEvaluateModel) -> tuple[list[EvaluateDocument], int]:
        pass