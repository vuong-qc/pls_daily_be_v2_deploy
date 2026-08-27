from beanie import PydanticObjectId

from src.models.template.request.filter_template_model import FilterTemplateModel
from src.repositories.template.template_repository import TemplateRepository
from src.models.user.user_document import UserDocument
from src.models.template.template_document import TemplateDocument
from beanie.operators import Set, In

class BeanieTemplateRepository(TemplateRepository):
    async def create_template(self, data: dict) -> TemplateDocument:
        template = TemplateDocument(**data)
        self._add_link_doc(data=data, template=template)
        await template.insert()
        return await TemplateDocument.get(template_id=template.id, fetch_links=True)

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
    async def get_template_by_id(self, template_id: str) -> TemplateDocument | None:
        return await TemplateDocument.get(template_id, fetch_links=True)
    async def get_list_templates(self, filters: FilterTemplateModel) -> tuple[list[TemplateDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", None)
        limit = filter_dump.pop("limit", None)
        if filters.status:
            filter_dump.update(In(TemplateDocument.status, filters.status))
        if filters.created_by:
            filter_dump.update(In(TemplateDocument.created_by, filters.created_by))
        query = TemplateDocument.find(filter_dump, fetch_links=True)
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