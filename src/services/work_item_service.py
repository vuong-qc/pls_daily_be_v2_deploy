from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.work_item.request.create_work_item_model import CreateWorkItemModel
from src.models.work_item.request.update_work_item_model import UpdateWorkItemModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.models.work_item.response.work_item_response_model import WorkItemResponse
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.exception.work_item_exception import WorkItemException, WorkItemStatusCode, WorkItemMessage

import logging
logger = logging.getLogger(__name__)



class WorkItemService:
    def __init__(self, work_item_repository: WorkItemRepository):
        self.work_item_repository = work_item_repository

    async def create_work_item_model(self, work_item_model: CreateWorkItemModel):
        work_item = await self.work_item_repository.create_work_item(work_item_model.model_dump())
        return ResponseModel(data=WorkItemResponse.model_validate(work_item))

    async def update_work_item_model(self, work_item_id:str, work_item_model: UpdateWorkItemModel):
        work_item = await self.work_item_repository.update_work_item(work_item_id,work_item_model.model_dump(exclude_unset=True))
        if not work_item:
            raise WorkItemException(WorkItemMessage.WORK_ITEM_NOT_FOUND, WorkItemStatusCode.WORK_ITEM_NOT_FOUND)
        return ResponseModel(data=WorkItemResponse.model_validate(work_item))

    async def delete_work_item_model(self, work_item_id:str):
        work_item = await self.work_item_repository.get_work_item_by_id(work_item_id)
        if not work_item:
            raise WorkItemException(WorkItemMessage.WORK_ITEM_NOT_FOUND, WorkItemStatusCode.WORK_ITEM_NOT_FOUND)
        await self.work_item_repository.delete_work_item(work_item_id)
        return ResponseModel()

    async def list_work_item_model(self, filters: FilterWorkItemModel):
        work_items, total = await self.work_item_repository.get_list_work_items(filters)
        list_response = []
        for work_item in work_items:
            work_item_response = WorkItemResponse.model_validate(work_item)
            list_response.append(work_item_response)
        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)
