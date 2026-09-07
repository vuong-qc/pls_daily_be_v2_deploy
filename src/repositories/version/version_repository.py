from abc import ABC, abstractmethod

from src.models.version.request.filter_version_model import FilterVersionModel
from src.models.version.version_document import VersionDocument


class VersionRepository(ABC):
    @abstractmethod
    async def get_version_by_id(self, version_id: str) -> VersionDocument | None:
        pass

    @abstractmethod
    async def create_version(self, data: dict) -> VersionDocument:
        pass

    @abstractmethod
    async def update_version(
        self, version_id: str, data: dict
    ) -> VersionDocument | None:
        pass

    @abstractmethod
    async def delete_version(self, version_id: str) -> bool:
        pass

    @abstractmethod
    async def get_list_versions(
        self, filters: FilterVersionModel, user_id: str
    ) -> tuple[list[VersionDocument], int]:
        pass
