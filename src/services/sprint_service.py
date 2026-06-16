import asyncio

from src.models.order.request.create_order_model import CreateOrderModel
from src.models.order.request.filter_order_model import FilterOrderModel
from src.models.order.request.update_order_model import UpdateOrderModel
from src.models.sprint.request.create_sprint_model import CreateSprintModel
from src.models.sprint.request.update_sprint_model import UpdateSprintModel
from src.repositories.order.order_repository import OrderRepository
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.services.user_service import UserService
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.services.project_service import ProjectService
from src.exception.sprint_exception import SprintException, SprintMessage, SprintStatusCode
from src.models.sprint.response.sprint_response_model import SprintResponse
from src.enums.work_item_type import WorkItemType
from src.enums.task_status_enum import TaskStatusEnum
import logging

from src.utils.lexorank_util import LexorankUtil

logger = logging.getLogger(__name__)

class SprintService:
    def __init__(self, sprint_repository: WorkItemRepository, user_service: UserService,
                 project_service: ProjectService, order_repository: OrderRepository, ):
        self.sprint_repository = sprint_repository
        self.user_service = user_service
        self.project_service = project_service
        self.order_repository = order_repository

    async def create_sprint(self, sprint_data: CreateSprintModel, handler_id:str = None):
        if sprint_data.assigned_id:
            for tasker in sprint_data.assigned_id:
                await self.user_service.get_user_by_id(tasker)
        if handler_id:
            await self._check_handler_of_project(sprint_data.parent, handler_id)
        else:
            await self.project_service.get_project_by_id(sprint_data.parent)
        sprint = await self.sprint_repository.create_work_item(sprint_data.model_dump())
        return ResponseModel(data=SprintResponse.model_validate(sprint))

    async def update_sprint(self, sprint_id:str, sprint_data: UpdateSprintModel, handler_id:str = None):
        if sprint_data.assigned_id:
            for tasker in sprint_data.assigned_id:
                await self.user_service.get_user_by_id(tasker)
        sprint = await self.sprint_repository.get_work_item_by_id(sprint_id)
        if handler_id:
            if sprint:
                await self._check_handler_of_project(sprint.parent, handler_id)
            else:
                raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)
        update_sprint = await self.sprint_repository.update_work_item(sprint_id,sprint_data.model_dump(exclude_unset=True))
        if update_sprint:
            response = SprintResponse.model_validate(update_sprint)
            if sprint_data.order_type:
                filter_order = FilterOrderModel(parent_id=sprint.parent, owner_id=handler_id, type=sprint_data.order_type,
                                                object_id=str(sprint.id))
                order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))

                if not order_model:
                    raise

                parent_id = sprint.parent
                update_data_order = UpdateOrderModel(type=sprint_data.order_type, parent_id=parent_id)
                updated_order = await self.order_repository.update_order(str(order_model.id),
                                                                         update_data_order.model_dump(
                                                                             exclude_unset=True),
                                                                         sprint_data.prev_order, sprint_data.next_order)
                response.order = updated_order.order if updated_order else updated_order
            else:
                filter_order = FilterOrderModel(parent_id=sprint.parent, owner_id=handler_id,
                                                object_id=str(sprint.id))
                order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))
                response.order = order_model.order if order_model else order_model
            return ResponseModel(data=response)
        raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)

    async def delete_sprint(self, sprint_id:str, handler_id:str):
        sprint = await self.sprint_repository.get_work_item_by_id(sprint_id)
        if sprint:
            await self._check_handler_of_project(sprint.parent, handler_id)
        else:
            raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)
        if sprint.type == WorkItemType.SPRINT:
            await self.sprint_repository.delete_work_item(sprint_id)
        else:
            raise SprintException(SprintMessage.DELETE_NOT_MATCH_TYPE, SprintStatusCode.DELETE_NOT_MATCH_TYPE)
        return ResponseModel()

    async def get_sprint_by_id(self, sprint_id:str):
        sprint = await self.sprint_repository.get_work_item_by_id(sprint_id)
        if sprint:
            return ResponseModel(data=SprintResponse.model_validate(sprint))
        raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)

    async def get_list_sprints(self, filters: FilterWorkItemModel, user_id:str):
        filter_order = FilterOrderModel(type=filters.type_order, owner_id=user_id, parent_id=filters.parent)

        list_response = []

        if filters.type_order:
            list_response, total = await LexorankUtil.auto_gen_order(filter_order, filters, SprintResponse, self.sprint_repository, self.order_repository)
        else:
            list_sprints, total = await self.sprint_repository.get_list_work_items(filters)
            for sprint_item in list_sprints:
                response = SprintResponse.model_validate(sprint_item)
                list_response.append(response)
        for response in list_response:
            if response.type == WorkItemType.SPRINT:
                await self._add_count_task_sprints(response, str(response.id))

        # if filters.type and len(filters.type) == 1 and WorkItemType.SPRINT in filters.type  :
        #     await asyncio.gather(*[
        #         self._add_count_task_sprints(sprint_item, str(sprint_item.id)) for sprint_item in list_response
        #     ])
        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

    async def _add_count_task_sprints(self, sprint_response: SprintResponse, parent:str):
        statistic = await self.sprint_repository.statistic_task(parent, WorkItemType.TASK.value, TaskStatusEnum.DONE.value)
        sprint_response.total_tasks = statistic.total_tasks
        sprint_response.done_tasks = statistic.target_status_tasks
        logger.info('data sprint: %s', sprint_response)


    async def _check_handler_of_project(self, project_id:str, handler_id:str):
        project = await self.sprint_repository.get_work_item_by_id(project_id)
        logger.info('check_handler_of_project: %s', project.handler_id)
        if handler_id not in project.handler_id:
            raise SprintException(SprintMessage.NOT_HANDLER_PR0JECT, SprintStatusCode.NOT_HANDLER_PR0JECT)
