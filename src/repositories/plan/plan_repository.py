from abc import ABC, abstractmethod
from src.models.plan.plan_document import PlanDocument
from src.models.plan.request.filter_plan_model import FilterPlanModel

class PlanRepository(ABC):
    @abstractmethod
    async def create_plan(self, data: dict)-> PlanDocument:
        pass
    @abstractmethod
    async def update_plan(self, plan_id: str, data: dict)-> PlanDocument|None:
        pass
    @abstractmethod
    async def delete_plan(self, plan_id: str):
        pass
    @abstractmethod
    async def get_plan_by_id(self, plan_id: str) -> PlanDocument| None:
        pass
    @abstractmethod
    async def get_list_plan(self, filters: FilterPlanModel) -> tuple[list[PlanDocument], int]:
        pass