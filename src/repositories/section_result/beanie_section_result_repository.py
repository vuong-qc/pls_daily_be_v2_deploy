from typing import Union

from beanie import PydanticObjectId
from beanie.operators import Set
from pymongo.errors import DuplicateKeyError

from src.models.section_result.section_result_document import SectionResultDocument
from src.models.user.user_document import UserDocument
from src.repositories.section_result.section_result_repository import SectionResultRepository
from src.utils.datetime_util import DateTimeUtil


class BeanieSectionResultRepository(SectionResultRepository):
    async def upsert_result(self, report_id: str, section_item_id: str, value: Union[float, str], created_by: str) -> tuple[SectionResultDocument, bool]:
        now = DateTimeUtil.current_milli_time()
        existing = await self.get_result(report_id, section_item_id)
        if existing:
            await existing.update(Set({"value": value, "updated_at": now}))
            return await self.get_result(report_id, section_item_id), False

        result = SectionResultDocument(
            report_id=report_id,
            section_item_id=section_item_id,
            value=value,
            created_by=created_by,
            creator_model=self._build_user_link(created_by),
            created_at=now,
            updated_at=now,
        )
        try:
            await result.insert()
            return await self.get_result(report_id, section_item_id), True
        except DuplicateKeyError:
            existing = await self.get_result(report_id, section_item_id)
            await existing.update(Set({"value": value, "updated_at": now}))
            return await self.get_result(report_id, section_item_id), False

    async def get_result(self, report_id: str, section_item_id: str) -> SectionResultDocument | None:
        return await SectionResultDocument.find_one(
            SectionResultDocument.report_id == report_id,
            SectionResultDocument.section_item_id == section_item_id,
            fetch_links=True,
        )

    async def get_results_by_report(self, report_id: str) -> list[SectionResultDocument]:
        return await SectionResultDocument.find(
            SectionResultDocument.report_id == report_id,
            fetch_links=True,
        ).to_list()

    def _build_user_link(self, user_id: str | None):
        if user_id and PydanticObjectId.is_valid(user_id):
            return UserDocument.model_construct(id=PydanticObjectId(user_id))
        return None
