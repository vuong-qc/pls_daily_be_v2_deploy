from abc import ABC, abstractmethod
from src.models.group.response.group_reponse_model import GroupResponse
from src.models.group.request.filter_group_model import FilterGroupModel
class GroupRepository(ABC):
    @abstractmethod
    async def create_group(self, data: dict)->GroupResponse:
        pass
    @abstractmethod
    async def update_group(self, group_id: str, data: dict)->GroupResponse|None:
        pass
    @abstractmethod
    async def delete_group(self, group_id: str):
        pass
    @abstractmethod
    async def get_list_of_groups(self, filters: FilterGroupModel) -> tuple[list[GroupResponse],int]:
        pass

    @abstractmethod
    async def get_group_by_id(self, group_id: str)->GroupResponse|None:
        pass
    @abstractmethod
    async def get_all_groups(self, filters: FilterGroupModel) -> tuple[list[GroupResponse],int]:
        pass