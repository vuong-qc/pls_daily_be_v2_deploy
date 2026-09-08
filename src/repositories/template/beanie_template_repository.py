from beanie import PydanticObjectId
from src.enums.template_status_enum import TemplateStatusEnum
from src.models.template.request.filter_template_model import FilterTemplateModel
from src.repositories.template.template_repository import TemplateRepository
from src.models.user.user_document import UserDocument
from src.models.template.template_document import TemplateDocument
from beanie.operators import Set, In, Or, Eq, And, RegEx
import re

class BeanieTemplateRepository(TemplateRepository):
    async def create_template(self, data: dict) -> TemplateDocument:
        template = TemplateDocument(**data)
        self._add_link_doc(data=data, template=template)
        await template.insert()
        return await TemplateDocument.get(template.id, fetch_links=True)

    async def update_template(self, template_id: str, data: dict) -> TemplateDocument | None:
        if PydanticObjectId.is_valid(template_id):
            template = await TemplateDocument.get(template_id)
            if template:
                await template.update(Set(data))
                return await TemplateDocument.get(template.id, fetch_links=True)
        return None
    async def delete_template(self, template_id: str) -> None:
        if PydanticObjectId.is_valid(template_id):
            template = await TemplateDocument.get(template_id)
            if template:
                await template.delete()
        return None
    async def get_template_by_id(self, template_id: str, ignore_deleted: bool = False) -> TemplateDocument | None:
        if ignore_deleted:
            if not PydanticObjectId.is_valid(template_id):
                return None
            return await TemplateDocument.find_many_in_all(
                {"_id": PydanticObjectId(template_id)},
                fetch_links=True,
            ).first_or_none()
        return await TemplateDocument.get(template_id, fetch_links=True)
    async def get_list_templates(self, filters: FilterTemplateModel, user_id: str) -> tuple[list[TemplateDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", None)
        limit = filter_dump.pop("limit", None)
        search = filter_dump.pop("search", None)
        filter_dump.pop("status", None)
        if filters.search:
            keyword = search.strip()
            filter_dump.update(
                RegEx(TemplateDocument.title, re.escape(keyword), "i"),
            )
        if filters.status:
            if TemplateStatusEnum.PUBLIC not in filters.status:
                filter_dump.update(
                    And(
                        Eq(TemplateDocument.created_by, user_id),
                        In(TemplateDocument.status, [status for status in filters.status]),
                    )
                )
            else:
                filter_dump.update(
                    Or(
                        And(
                            Eq(TemplateDocument.created_by, user_id),
                            In(TemplateDocument.status, [status for status in filters.status if status != TemplateStatusEnum.PUBLIC]),
                        ),
                        Eq(TemplateDocument.status, TemplateStatusEnum.PUBLIC),
                    )
                )
        else:
            filter_dump.update(
                    Eq(TemplateDocument.status, TemplateStatusEnum.PUBLIC),
            )
        if filters.created_by:
            filter_dump.update(
                And(
                    In("created_by", filters.created_by),
                    Eq("status", TemplateStatusEnum.PUBLIC)
                )
            )
        if not filters.created_by and not filters.status:
            filter_dump.update(
                Or(
                    Eq(TemplateDocument.created_by, user_id),
                    Eq(TemplateDocument.status, TemplateStatusEnum.PUBLIC),
                )
            )
        print("filter_dump", filter_dump)
        query = TemplateDocument.find(filter_dump, fetch_links=True).sort("+position")
        count = await query.count()
        if offset and limit:
            list_template = await query.skip(offset).limit(limit).to_list()
            return list_template, count
        list_template = await query.to_list()
        return list_template, count
    def _add_link_doc(self, data: dict, template: TemplateDocument):
        created_by = data.pop("created_by", None)
        if created_by and PydanticObjectId.is_valid(created_by):
            template.creator_model = UserDocument.model_construct(id=PydanticObjectId(created_by))
    async def get_latest_template(self, group: str) -> TemplateDocument | None:
        query = TemplateDocument.find(Eq(TemplateDocument.group, group), fetch_links=True).sort("-position")
        template= await query.limit(1).to_list()
        return template[0] if template else None