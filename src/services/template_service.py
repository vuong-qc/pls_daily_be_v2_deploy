from src.enums.template_status_enum import TemplateStatusEnum
from src.models.template.request.create_template_model import CreateTemplateModel
from src.models.template.response.template_response_model import TemplateResponseModel
from src.models.template.request.filter_template_model import FilterTemplateModel
from src.models.template.request.update_template_model import UpdateTemplateModel
from src.repositories.template.template_repository import TemplateRepository
from src.exception.template_exception import TemplateException, TemplateStatusCode, TemplateMessage
from src.services.group_service import GroupService

class TemplateService:
    def __init__(self, template_repository: TemplateRepository, group_service: GroupService):
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

    async def create_template(self, template: CreateTemplateModel, user_id:str)-> TemplateResponseModel:
        template.created_by = user_id
        await self.group_service.get_group_by_id(template.group)
        new_template = await self.template_repository.create_template(template.model_dump())
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

    async def get_list_templates(self, filters: FilterTemplateModel)-> tuple[list[TemplateResponseModel], int]:
        list_template, total = await self.template_repository.get_list_templates(filters)
        list_response = []
        for template in list_template:
            list_response.append(TemplateResponseModel.model_validate(template))
        return list_response, total
