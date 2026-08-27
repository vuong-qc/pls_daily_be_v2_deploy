from src.services.template_service import TemplateService
from src.models.template.request.create_template_model import CreateTemplateModel
from src.models.template.request.filter_template_model import FilterTemplateModel
from src.models.template.request.update_template_model import UpdateTemplateModel
from src.repositories.template.beanie_template_repository import BeanieTemplateRepository
from typing import Annotated
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.routes.group_route import get_group_service, GroupService
from fastapi import APIRouter, Depends, Query, status
from src.utils.proxy_util import get_current_user_by_token

router = APIRouter(
    tags=["template"],
)

def get_template_service(
        group_service: GroupService = Depends(get_group_service),
):
    template_repository = BeanieTemplateRepository()
    return TemplateService(template_repository, group_service)

@router.get("/get-list-template",
            response_model=ResponsePaginatedModel,
            status_code=status.HTTP_200_OK,
            summary="Get a list of templates")
async def get_list_template(
        query: Annotated[FilterTemplateModel, Query()],
        service: TemplateService = Depends(get_template_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    list_data, total = await service.get_list_templates(query)
    return ResponsePaginatedModel(data=list_data, total=total,offset=query.offset if query.offset is not None else 0)

@router.post("/create-template",
             response_model=ResponseModel,
              status_code=status.HTTP_201_CREATED,
             summary="Create a new template")
async def create_template(
        template: CreateTemplateModel,
        service: TemplateService = Depends(get_template_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data['sub']
    response = await service.create_template(template, user_id)
    return ResponseModel(data=response)
@router.put("/update-template/{template_id}",
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            summary="Update a template")
async def update_template(
        template_id: str,
        template_data: UpdateTemplateModel,
        service: TemplateService = Depends(get_template_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    response = await service.update_template(template_id, template_data, user_data["sub"])
    return ResponseModel(data=response)

@router.delete("/delete-template/{template_id}",
                status_code=status.HTTP_204_NO_CONTENT,
                summary="Delete a template" )
async def delete_template(
        template_id: str,
        service: TemplateService = Depends(get_template_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    response = await service.delete_template(template_id, user_data["sub"])
