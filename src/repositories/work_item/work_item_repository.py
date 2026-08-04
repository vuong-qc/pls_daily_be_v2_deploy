from abc import ABC, abstractmethod
from typing import Optional

from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.models.work_item.work_item_document import WorkItemDocument, SprintTaskStatsResult

class WorkItemRepository(ABC):
    @abstractmethod
    async def create_work_item(self, data: dict)->WorkItemDocument:
        pass

    @abstractmethod
    async def update_work_item(self,project_id:str, data: dict)->WorkItemDocument|None:
        pass
    @abstractmethod
    async def delete_work_item(self,project_id:str)->None:
        pass
    @abstractmethod
    async def get_list_work_items(self, filters: FilterWorkItemModel)->tuple[list[WorkItemDocument], int]:
        pass

    @abstractmethod
    async def get_work_item_by_id(self, project_id:str)->WorkItemDocument|None:
        pass

    @abstractmethod
    async def count_work_item(self, filters: FilterWorkItemModel)->int:
        pass

    @abstractmethod
    async def get_children(self, parent_id:str, status: Optional[list[str]]= None, user_id: Optional[str]= None) ->list[WorkItemDocument]:
        pass

    @abstractmethod
    async def get_children_by_parents(self, parents: list[str], status: Optional[list[str]]= None, user_id: Optional[list[str]]= None):
        pass

    @abstractmethod
    async def statistic_task(self, sprint_ids:list[str], type:str, target_status:list[str])-> SprintTaskStatsResult | None:
        pass

    @abstractmethod
    async def filter_work_item_for_order(self, filters: FilterWorkItemModel)->list[WorkItemDocument]:
        pass

    @abstractmethod
    async def update_many(self, list_ids: list[str], data: dict):
        pass
    @abstractmethod
    async def count_items_by_parent_status(
                self,
                parents: list[str],
                statuses: list[str],
        ) -> dict[str, dict[str, int]]:
        pass

    @abstractmethod
    async def count_point(self, filters: FilterWorkItemModel)->float:
        pass
    @abstractmethod
    async def statistic_bug(self, filters: FilterWorkItemModel) -> dict:
        pass
    @abstractmethod
    async def count_total_tasks_in_sprint(self, filters: FilterWorkItemModel) -> int: pass
    @abstractmethod
    async def count_by_time_buckets(
            self,
            filters: FilterWorkItemModel
    ) -> dict: pass
    @abstractmethod
    async def sum_point_by_time_buckets(
            self,
            filters: FilterWorkItemModel
    ) -> dict: pass