import re

from beanie import PydanticObjectId
from beanie.operators import In, Set

from src.models.section.section_document import SectionDocument
from src.repositories.section.section_repository import SectionRepository


class BeanieSectionRepository(SectionRepository):
    async def create_section(self, data: dict) -> SectionDocument:
        section = SectionDocument(**data)
        await section.insert()
        return section

    async def get_section_by_id(self, section_id: str) -> SectionDocument | None:
        if not PydanticObjectId.is_valid(section_id):
            return None
        return await SectionDocument.get(section_id)

    async def get_sections_by_parent_id(self, parent_id: str, section_type: str) -> list[SectionDocument]:
        return await SectionDocument.find(
            SectionDocument.parent_id == parent_id,
            SectionDocument.type == section_type,
        ).sort("+position").to_list()

    async def get_sections_by_parent_ids(self, parent_ids: list[str], section_type: str) -> list[SectionDocument]:
        if not parent_ids:
            return []
        return await SectionDocument.find(
            In(SectionDocument.parent_id, parent_ids),
            SectionDocument.type == section_type,
        ).sort("+position").to_list()

    async def update_section(self, section_id: str, data: dict) -> SectionDocument | None:
        section = await self.get_section_by_id(section_id)
        if section:
            await section.update(Set(data))
            return await SectionDocument.get(section.id)
        return None

    async def delete_section(self, section_id: str) -> None:
        section = await self.get_section_by_id(section_id)
        if section:
            await section.delete()

    async def get_sections(
            self,
            list_type: list[str] | None = None,
            parent_ids: list[str] | None = None,
            categories: list[str] | None = None,
            value_types: list[str] | None = None,
            search: str | None = None,
    ) -> list[SectionDocument]:
        filters = {}

        if list_type:
            filters["type"] = {"$in": list_type}

        if parent_ids:
            filters["parent_id"] = {"$in": parent_ids}

        if categories:
            filters["category"] = {"$in": categories}

        if value_types:
            filters["value_type"] = {"$in": value_types}

        if search := (search or "").strip():
            pattern = re.escape(search)
            filters["$or"] = [
                {
                    "title": {
                        "$regex": pattern,
                        "$options": "i",
                    }
                },
                {
                    "description": {
                        "$regex": pattern,
                        "$options": "i",
                    }
                },
            ]

        return await SectionDocument.find(filters).sort("+position").to_list()
