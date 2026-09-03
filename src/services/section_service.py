from collections import defaultdict

from src.enums.section_enum import SectionTypeEnum, SectionValueTypeEnum
from src.enums.template_status_enum import TemplateStatusEnum
from src.exception.section_exception import SectionException, SectionMessage, SectionStatusCode
from src.exception.template_exception import TemplateException, TemplateMessage, TemplateStatusCode
from src.models.section.request.section_model import CreateSectionItemModel, CreateSectionModel, UpdateSectionModel
from src.models.section.response.section_response_model import SectionResponseModel
from src.repositories.section.section_repository import SectionRepository
from src.repositories.template.template_repository import TemplateRepository
from src.utils.datetime_util import DateTimeUtil
from src.utils.lexorank_util import LexorankUtil


class SectionService:
    def __init__(self, section_repository: SectionRepository, template_repository: TemplateRepository):
        self.section_repository = section_repository
        self.template_repository = template_repository
        self.section_types = {value.value for value in SectionTypeEnum}
        self.value_types = {value.value for value in SectionValueTypeEnum}

    async def create_section(self, template_id: str, data: CreateSectionModel, user_id: str) -> SectionResponseModel:
        await self._get_editable_template(template_id, user_id)
        section_data = data.model_dump()
        section_data["position"] = self._build_position(section_data)
        section_data.update(type=SectionTypeEnum.SECTION, parent_id=template_id)
        return SectionResponseModel.model_validate(await self.section_repository.create_section(section_data))

    async def create_section_item(self, section_id: str, data: CreateSectionItemModel, user_id: str) -> SectionResponseModel:
        parent = await self.section_repository.get_section_by_id(section_id)
        if not parent:
            raise SectionException(SectionMessage.NOT_FOUND, SectionStatusCode.NOT_FOUND)
        if parent.type != SectionTypeEnum.SECTION:
            raise SectionException(SectionMessage.INVALID_PARENT, SectionStatusCode.INVALID_PARENT)
        await self._get_editable_template(parent.parent_id, user_id)
        if data.value_type not in self.value_types:
            raise SectionException(SectionMessage.INVALID_VALUE_TYPE, SectionStatusCode.INVALID_VALUE_TYPE)
        item_data = data.model_dump()
        item_data["position"] = self._build_position(item_data)
        item_data.update(type=SectionTypeEnum.ITEM, parent_id=section_id)
        return SectionResponseModel.model_validate(await self.section_repository.create_section(item_data))

    async def update_section(self, section_id: str, data: UpdateSectionModel, user_id: str) -> SectionResponseModel:
        section = await self._get_section(section_id)
        template_id = section.parent_id
        if section.type == SectionTypeEnum.ITEM:
            parent = await self._get_section(section.parent_id)
            template_id = parent.parent_id
        await self._get_editable_template(template_id, user_id)
        update_data = data.model_dump(exclude_unset=True)
        if "prev_order" in update_data or "next_order" in update_data:
            update_data["position"] = self._build_position(update_data)
        if "value_type" in update_data and update_data["value_type"] not in self.value_types:
            raise SectionException(SectionMessage.INVALID_VALUE_TYPE, SectionStatusCode.INVALID_VALUE_TYPE)
        update_data["updated_at"] = DateTimeUtil.current_milli_time()
        return SectionResponseModel.model_validate(await self.section_repository.update_section(section_id, update_data))

    async def delete_section(self, section_id: str, user_id: str) -> None:
        section = await self._get_section(section_id)
        template_id = section.parent_id
        if section.type == SectionTypeEnum.ITEM:
            template_id = (await self._get_section(section.parent_id)).parent_id
        await self._get_editable_template(template_id, user_id)
        await self.section_repository.delete_section(section_id)

    async def get_section_tree(self, template_id: str) -> list[SectionResponseModel]:
        sections = await self.section_repository.get_sections_by_parent_id(template_id, SectionTypeEnum.SECTION)
        section_ids = [str(section.id) for section in sections]
        items = await self.section_repository.get_sections_by_parent_ids(section_ids, SectionTypeEnum.ITEM)
        items_by_parent = defaultdict(list)
        for item in items:
            items_by_parent[item.parent_id].append(SectionResponseModel.model_validate(item))
        return [
            SectionResponseModel.model_validate(section).model_copy(
                update={"items": items_by_parent[str(section.id)]}
            )
            for section in sections
        ]

    async def _get_section(self, section_id: str):
        section = await self.section_repository.get_section_by_id(section_id)
        if not section:
            raise SectionException(SectionMessage.NOT_FOUND, SectionStatusCode.NOT_FOUND)
        return section

    async def _get_editable_template(self, template_id: str, user_id: str):
        template = await self.template_repository.get_template_by_id(template_id)
        if not template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)
        if template.created_by != user_id:
            raise TemplateException(TemplateMessage.NOT_OWNER, TemplateStatusCode.NOT_OWNER)
        if template.status != TemplateStatusEnum.DRAFT:
            raise SectionException(SectionMessage.TEMPLATE_NOT_EDITABLE, SectionStatusCode.TEMPLATE_NOT_EDITABLE)
        return template

    @staticmethod
    def _build_position(data: dict) -> str:
        prev_order = data.pop("prev_order", None)
        next_order = data.pop("next_order", None)
        return LexorankUtil.get_lexorank_between(prev_order, next_order)

    async def get_sections(
            self,
            list_type: list[str] | None = None,
            parent_ids: list[str] | None = None,
            categories: list[str] | None = None,
            value_types: list[str] | None = None,
            search: str | None = None,
    ) -> list[SectionResponseModel]:
        if list_type:
            invalid_types = [value for value in list_type if value not in SectionTypeEnum]
            if invalid_types:
                raise SectionException(SectionMessage.INVALID_TYPE, SectionStatusCode.INVALID_TYPE)

        if value_types:
            invalid_value_types = [value for value in value_types if value not in SectionValueTypeEnum]
            if invalid_value_types:
                raise SectionException(SectionMessage.INVALID_VALUE_TYPE, SectionStatusCode.INVALID_VALUE_TYPE)

        sections = await self.section_repository.get_sections(
            list_type=list_type,
            parent_ids=parent_ids,
            categories=categories,
            value_types=value_types,
            search=search,
        )

        section_ids = {
            str(section.id)
            for section in sections
            if section.type == SectionTypeEnum.SECTION
        }

        items = await self.section_repository.get_sections_by_parent_ids(
            list(section_ids),
            SectionTypeEnum.ITEM,
        )

        items_by_parent = defaultdict(list)

        for item in items:
            items_by_parent[item.parent_id].append(
                SectionResponseModel.model_validate(item)
            )

        return [
            SectionResponseModel.model_validate(section).model_copy(
                update={"items": items_by_parent[str(section.id)]}
            )
            for section in sections
            if not (
                    section.type == SectionTypeEnum.ITEM
                    and section.parent_id in section_ids
            )
        ]