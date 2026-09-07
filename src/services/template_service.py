from src.enums.section_enum import SectionTypeEnum
from src.enums.template_status_enum import TemplateStatusEnum
from src.models.template.request.create_template_model import CreateTemplateModel, CreateDuplicateTemplateModel
from src.models.template.response.template_response_model import TemplateResponseModel
from src.models.template.request.filter_template_model import FilterTemplateModel
from src.models.template.request.update_template_model import UpdateTemplateModel
from src.repositories.template.template_repository import TemplateRepository
from src.repositories.section.section_repository import SectionRepository
from src.exception.template_exception import TemplateException, TemplateStatusCode, TemplateMessage
from src.services.group_service import GroupService
from src.utils.lexorank_util import LexorankUtil

class TemplateService:
    def __init__(self, template_repository: TemplateRepository, group_service: GroupService, section_repository: SectionRepository):
        self.template_repository = template_repository
        self.group_service = group_service
        self.allow_field = {"status"}
        self.allowed_status_transitions = {
            TemplateStatusEnum.DRAFT: {
                TemplateStatusEnum.DISABLED,
                TemplateStatusEnum.PUBLIC,
            },
            TemplateStatusEnum.DISABLED: {TemplateStatusEnum.PUBLIC},
            TemplateStatusEnum.PUBLIC: {TemplateStatusEnum.DISABLED},
        }
        self.section_repository = section_repository

    async def create_template(self, template: CreateTemplateModel, user_id:str)-> TemplateResponseModel:
        template.created_by = user_id
        await self.group_service.get_group_by_id(template.group)
        template_data = template.model_dump()
        template_data["position"] = self._build_position(template_data)
        new_template = await self.template_repository.create_template(template_data)
        response = TemplateResponseModel.model_validate(new_template)
        return response

    async def get_template(self, template_id: str) -> TemplateResponseModel:
        template = await self.template_repository.get_template_by_id(template_id)
        if not template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)
        return TemplateResponseModel.model_validate(template)

    async def update_template(self, template_id:str,  template_data: UpdateTemplateModel, user_id:str)-> TemplateResponseModel:
        template = await self.template_repository.get_template_by_id(template_id)
        if not template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)
        if template.created_by != user_id:
            raise TemplateException(TemplateMessage.NOT_OWNER, TemplateStatusCode.NOT_OWNER)
        data_dump = template_data.model_dump(exclude_unset=True)
        if "prev_order" in data_dump or "next_order" in data_dump:
            data_dump["position"] = self._build_position(data_dump)
        change_field = set(data_dump.keys())
        if change_field - self.allow_field and template.status != TemplateStatusEnum.DRAFT:
            raise TemplateException(TemplateMessage.CAN_NOT_MODIFY, TemplateStatusCode.CAN_NOT_MODIFY)
        if template_data.status is not None:
            allowed_targets = self.allowed_status_transitions.get(template.status, set())
            if data_dump["status"] not in allowed_targets:
                raise TemplateException(
                    TemplateMessage.STATUS_INVALID,
                    TemplateStatusCode.STATUS_INVALID,
                )
        updated_template = await self.template_repository.update_template(template_id, data_dump)
        response = TemplateResponseModel.model_validate(updated_template)
        return response
    async def delete_template(self, template_id:str, user_id:str):
        template = await self.template_repository.get_template_by_id(template_id)
        if not template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)
        if template.created_by != user_id:
            raise TemplateException(TemplateMessage.NOT_OWNER, TemplateStatusCode.NOT_OWNER)
        await self.template_repository.delete_template(template_id)

    async def get_list_templates(self, filters: FilterTemplateModel, user_id: str)-> tuple[list[TemplateResponseModel], int]:
        list_template, total = await self.template_repository.get_list_templates(filters, user_id)
        list_response = []
        for template in list_template:
            list_response.append(TemplateResponseModel.model_validate(template))
        return list_response, total

    def _build_position(self, data: dict) -> str:
        prev_order = data.pop("prev_order", None)
        next_order = data.pop("next_order", None)
        return LexorankUtil.get_lexorank_between(prev_order, next_order)

    async def duplicate_template(self, data: CreateDuplicateTemplateModel, user_id: str) -> TemplateResponseModel:
        await self.group_service.get_group_by_id(data.group)
        original_template = await self.template_repository.get_template_by_id(data.template_id)
        if not original_template:
            raise TemplateException(TemplateMessage.NOT_FOUND, TemplateStatusCode.NOT_FOUND)

        template_cp = original_template.model_copy(deep=True)
        template_cp.created_by = user_id
        template_cp.group = data.group
        latest_template = await self.template_repository.get_latest_template(data.group)
        prev_order = latest_template.position if latest_template else None
        next_order = None

        template_cp.position = LexorankUtil.get_lexorank_between(prev_order, next_order)
        template_data = template_cp.model_dump(exclude={"created_at, updated_at"})
        template_data.pop("id", None)

        new_template = await self.template_repository.create_template(template_data)
        sections = await self.section_repository.get_sections_by_parent_id(data.template_id, SectionTypeEnum.SECTION)
        for section in sections:
            copy_sec = section.model_copy(deep=True)
            copy_sec.parent_id = str(new_template.id)
            items = await self.section_repository.get_sections_by_parent_ids([str(section.id)], SectionTypeEnum.ITEM)

            new_section = await self.section_repository.create_section(copy_sec.model_dump(exclude={"created_at, updated_at", "id"}))
            list_items = []
            for item in items:
                copy_item = item.model_copy(deep=True)
                copy_item.parent_id = str(new_section.id)
                copy_item_draw = copy_item.model_dump(exclude={"created_at, updated_at", "id"})
                list_items.append(copy_item_draw)
            await self.section_repository.create_many_section(list_items)
        response = TemplateResponseModel.model_validate(new_template)
        return response