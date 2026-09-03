from abc import ABC, abstractmethod

from src.models.section.section_document import SectionDocument


class SectionRepository(ABC):
    @abstractmethod
    async def create_section(self, data: dict) -> SectionDocument: ...

    @abstractmethod
    async def get_section_by_id(self, section_id: str) -> SectionDocument | None: ...

    @abstractmethod
    async def get_sections_by_parent_id(self, parent_id: str, section_type: str) -> list[SectionDocument]: ...

    @abstractmethod
    async def get_sections_by_parent_ids(self, parent_ids: list[str], section_type: str) -> list[SectionDocument]: ...

    @abstractmethod
    async def update_section(self, section_id: str, data: dict) -> SectionDocument | None: ...

    @abstractmethod
    async def delete_section(self, section_id: str) -> None: ...

    @abstractmethod
    async def get_sections(
            self,
            list_type: list[str] | None = None,
            parent_ids: list[str] | None = None,
            categories: list[str] | None = None,
            value_types: list[str] | None = None,
            search: str | None = None,
    ) -> list[SectionDocument]: pass
