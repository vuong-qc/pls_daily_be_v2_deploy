from src.services.work_item_service import WorkItemService
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.models.work_item.request.create_work_item_model import CreateWorkItemModel
from src.models.work_item.request.update_work_item_model import UpdateWorkItemModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.utils.proxy_util import get_current_user_by_token
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated

router = APIRouter(
    tags = ['work-item']
)

def get_work_item_service():
    beanie_work_item_repository = BeanieWorkItemRepository()
    return WorkItemService(beanie_work_item_repository)

@router.post('/create-work-item',
             summary='Create a new work item',
             description='Create a new work item',
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             )
async def create_work_item_model(work_item_model: CreateWorkItemModel,
                           service: WorkItemService = Depends(get_work_item_service),
                           user_data: dict = Depends(get_current_user_by_token),
                           ):
    user_id = user_data.get('sub')
    work_item_model.owner_id = user_id
    return await service.create_work_item_model(work_item_model)

@router.put('/update-work-item/{id}',
             summary='Update a work item',
             description='Update a work item',
             status_code=status.HTTP_202_ACCEPTED,
             response_model=ResponseModel,
             )
async def update_work_item_model(
        work_item_id: str,
        work_item_model: UpdateWorkItemModel,
        service: WorkItemService = Depends(get_work_item_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await service.update_work_item_model(work_item_id, work_item_model)

@router.delete('/delete-work-item/{work_id}',

               summary='Delete a work item',
               description='Delete a work item',
               status_code=status.HTTP_204_NO_CONTENT,)
async def delete_work_item_model(
        work_id: str,
        service: WorkItemService = Depends(get_work_item_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await service.delete_work_item_model(work_id)

@router.get('/get-list-work-items',
            summary='List all work items',
            description='List all work items',
            status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel,
            )
async def get_list_work_items(
        filters: Annotated[FilterWorkItemModel, Query()],
        service: WorkItemService = Depends(get_work_item_service),
        # user_data: dict = Depends(get_current_user_by_token)
):
    return await service.list_work_item_model(filters)

@router.post('/create-work-item-guest',
             summary='Create a new work item for guest user',
             description='Create a new work item by guest user',
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             )
async def create_work_item_model(work_item_model: CreateWorkItemModel,
                           service: WorkItemService = Depends(get_work_item_service),
                           ):
    return await service.create_work_item_model(work_item_model)