from beanie import PydanticObjectId
from beanie.operators import And, Eq, In, Or, Set

from src.models.user.user_document import UserDocument
from src.models.version.request.filter_version_model import FilterVersionModel
from src.models.version.version_document import VersionDocument
from src.repositories.version.version_repository import VersionRepository
from src.enums.version_type_enum import VersionTypeEnum


class BeanieVersionRepository(VersionRepository):
    async def get_version_by_id(self, version_id: str) -> VersionDocument | None:
        if not PydanticObjectId.is_valid(version_id):
            return None
        return await VersionDocument.get(version_id, fetch_links=True)

    async def create_version(self, data: dict) -> VersionDocument:
        version = VersionDocument(**data)
        self._add_creator_link(version, data)
        await version.insert()
        return await VersionDocument.get(version.id, fetch_links=True)

    async def update_version(self, version_id: str, data: dict) -> VersionDocument | None:
        if not PydanticObjectId.is_valid(version_id):
            return None
        version = await VersionDocument.get(version_id, fetch_links=True)
        if not version:
            return None
        self._add_creator_link(version, data)
        await version.save()
        await version.update(Set(data))
        return await VersionDocument.get(version_id, fetch_links=True)

    async def delete_version(self, version_id: str) -> bool:
        if not PydanticObjectId.is_valid(version_id):
            return False
        version = await VersionDocument.get(version_id)
        if not version:
            return False
        await version.delete()
        return True

    async def get_list_versions(
        self, filters: FilterVersionModel, user_id: str
    ) -> tuple[list[VersionDocument], int]:
        query_data = filters.model_dump(exclude_unset=True)
        offset = query_data.pop("offset", 0)
        limit = query_data.pop("limit", 10)

        version_types = query_data.pop("type", None)
        if version_types and VersionTypeEnum.PERSONAL in version_types:
            query_data.update(
                Or(
                    And(
                        Eq(VersionDocument.type, VersionTypeEnum.PERSONAL),
                        Eq(VersionDocument.creator_id, user_id),
                    ),
                    In(
                        VersionDocument.type,
                        [
                            version_type
                            for version_type in version_types
                            if version_type != VersionTypeEnum.PERSONAL
                        ],
                    ),
                )
            )
        elif version_types:
            query_data.update(In(VersionDocument.type, version_types))
        else:
            query_data.update(
                And(
                    Eq(VersionDocument.type, VersionTypeEnum.PERSONAL),
                    Eq(VersionDocument.creator_id, user_id),
                )
            )

        object_ids = query_data.pop("object_id", None)
        if object_ids:
            query_data.update(In(VersionDocument.object_id, object_ids))

        query = VersionDocument.find(query_data, fetch_links=True)
        total = await query.count()
        versions = await (
            query.sort("-created_at", "-_id")
            .skip(offset)
            .limit(limit)
            .to_list(length=limit)
        )
        return versions, total

    @staticmethod
    def _add_creator_link(version: VersionDocument, data: dict) -> None:
        creator_id = data.get("creator_id")
        updator_id = data.get("updator_id")
        if creator_id and PydanticObjectId.is_valid(creator_id):
            version.creator_model = UserDocument.model_construct(
                id=PydanticObjectId(creator_id)
            )
        if updator_id and PydanticObjectId.is_valid(updator_id):
            version.updator_model = UserDocument.model_construct(
                id=PydanticObjectId(updator_id)
            )
