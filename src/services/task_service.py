from src.enums.work_item_type import WorkItemType
from src.models.task.request.create_task_model import CreateTaskModel, CreateUserTaskModel, CreateStoryModel
from src.models.task.request.update_task_model import UpdateTaskModel, UpdateUserTaskModel, UpdateStoryModel
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.services.user_service import UserService
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.services.project_service import ProjectService
from src.exception.task_exception import TaskException, TaskMessage, TaskStatusCode
from src.models.task.response.task_response_model import TaskResponse
from src.models.subtask.request.create_subtask_model import CreateSubtaskModel
from src.models.subtask.request.update_subtask_model import UpdateSubtaskModel
from src.exception.sprint_exception import SprintException, SprintMessage, SprintStatusCode
from src.exception.project_exception import ProjectException, ProjectMessage, ProjectStatusCode
from src.models.order.request.create_order_model import CreateOrderModel
from src.utils.lexorank_util import LexorankUtil
from src.models.task.request.filter_task_model import FilterTaskModel
from src.models.order.request.update_order_model import UpdateOrderModel
from src.models.order.request.filter_order_model import FilterOrderModel
from src.repositories.order.order_repository import OrderRepository
import asyncio
import logging
logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, task_repository: WorkItemRepository, user_service: UserService, project_service: ProjectService, order_repository: OrderRepository):
        self.task_repository = task_repository
        self.user_service = user_service
        self.project_service = project_service
        self.order_repository = order_repository

    async def create_task(self, task_data: CreateTaskModel, handler_id:str = None):
        if task_data.assigned_id:
            for tasker in task_data.assigned_id:
                await self.user_service.get_user_by_id(tasker)
        # sprint or backlog or story
        sprint = await self.task_repository.get_work_item_by_id(task_data.parent)
        if not sprint:
            raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)
        # check sprint not found
        if handler_id:
            if sprint.type == WorkItemType.SPRINT or sprint.type == WorkItemType.BACKLOG:
                await self._check_handler_of_project(sprint.parent, handler_id)
            #case story
            if sprint.type == WorkItemType.STORY:
                #get sprint/backlog
                parent = await self.task_repository.get_work_item_by_id(sprint.parent)
                if parent:
                    await self._check_handler_of_project(parent.parent, handler_id)

        task = await self.task_repository.create_work_item(task_data.model_dump())
        return ResponseModel(data=TaskResponse.model_validate(task))

    async def update_task(self, task_id:str, task_data: UpdateTaskModel, handler_id:str = None):
        if task_data.assigned_id:
            for tasker in task_data.assigned_id:
                await self.user_service.get_user_by_id(tasker)

        task = await self.task_repository.get_work_item_by_id(task_id)
        if not task:
            raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
        if handler_id:
            sprint = await self.task_repository.get_work_item_by_id(task.parent)
            if sprint.type == WorkItemType.SPRINT or sprint.type == WorkItemType.BACKLOG:
                await self._check_handler_of_project(sprint.parent, handler_id)
            # case story
            if sprint.type == WorkItemType.STORY:
                # get sprint/backlog
                # check param type exist => raise error
                if task_data.type and task_data.type != WorkItemType.TASK:
                    raise TaskException(TaskMessage.NOT_UPDATE_TASK_TYPE_IN_STORY, TaskStatusCode.NOT_UPDATE_TASK_TYPE_IN_STORY)
                parent = await self.task_repository.get_work_item_by_id(sprint.parent)
                if parent:
                    await self._check_handler_of_project(parent.parent, handler_id)
        # check task has subtask, if update type != task => raise error
        if task_data.type and task_data.type != WorkItemType.TASK:
            # count children
            filters = FilterWorkItemModel(parent=task_id, offset=0, limit=1,type=[WorkItemType.SUBTASK])
            count = await self.task_repository.count_work_item(filters)
            if count > 0:
                raise TaskException(TaskMessage.NOT_CHANGE_TYPE_ITEM_HAS_CHILDREN, TaskStatusCode.NOT_CHANGE_TYPE_ITEM_HAS_CHILDREN)

        update_data = task_data.model_dump(exclude_unset=True)

        update_task = await self.task_repository.update_work_item(task_id,update_data)
        if update_task:
            response = TaskResponse.model_validate(update_task)

            if task_data.order_type:
                filter_order = FilterOrderModel(parent_id=task.parent, owner_id=handler_id, type=task_data.order_type,
                                                object_id=task_id)
                order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))

                if not order_model:
                    raise

                parent_id = task_data.parent if task_data.parent else task.parent
                update_data_order = UpdateOrderModel(type=task_data.order_type, parent_id=parent_id)
                updated_order = await self.order_repository.update_order(str(order_model.id),
                                                         update_data_order.model_dump(exclude_unset=True),
                                                         task_data.prev_order, task_data.next_order)
                response.order = updated_order.order if updated_order else updated_order
            else:
                filter_order = FilterOrderModel(parent_id=task.parent, owner_id=handler_id,
                                                object_id=task_id)
                order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))
                response.order = order_model.order if order_model else order_model

            return ResponseModel(data=response)
        raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)

    async def delete_task(self, task_id:str, handler_id:str):
        task = await self.task_repository.get_work_item_by_id(task_id)
        if task:
            sprint = await self.task_repository.get_work_item_by_id(task.parent)
            # check parent of task is print or story
            if sprint.type == WorkItemType.SPRINT or sprint.type == WorkItemType.BACKLOG:
                await self._check_handler_of_project(sprint.parent, handler_id)
            elif sprint.type == WorkItemType.STORY:
                work_item = await self.task_repository.get_work_item_by_id(sprint.parent)
                await self._check_handler_of_project(work_item.parent, handler_id)
        else:
            raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
        await self.task_repository.delete_work_item(task_id)

    async def get_task_by_id(self, task_id:str):
        task = await self.task_repository.get_work_item_by_id(task_id)
        if task:
            return ResponseModel(data=TaskResponse.model_validate(task))
        raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)

    async def get_list_tasks(self, filters: FilterTaskModel, user_id: str):
        filter_order = FilterOrderModel(type=filters.type_order, owner_id=user_id, parent_id=filters.parent)

        # case task
        if filters.type_order:
            list_response, total = await self._auto_gen_order(filter_order, filters)
            return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

        list_response = []
        list_tasks, total = await self.task_repository.get_list_work_items(filters)
        for task in list_tasks:
            list_response.append(TaskResponse.model_validate(task))
        if filters.type and (WorkItemType.STORY in filters.type or WorkItemType.BACKLOG in filters.type):
            await asyncio.gather(*[
                self._get_task_story(
                    task
                )
                for task in list_response
            ])
        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

    async def create_subtask(self, data: CreateSubtaskModel, user_id: str):
        # check user is assigned to task to create subtask
        task = await self.task_repository.get_work_item_by_id(data.parent)
        if task:
            if not task.assigned_id or user_id not in task.assigned_id:
                raise TaskException(TaskMessage.TASKER_NOT_MATCH_TASK, TaskStatusCode.TASKER_NOT_MATCH_TASK)

        subtask = await self.task_repository.create_work_item(data.model_dump())
        return ResponseModel(data=TaskResponse.model_validate(subtask))

    async def update_subtask(self, subtask_id:str, data: UpdateSubtaskModel, user_id: str):
        subtask = await self.task_repository.get_work_item_by_id(subtask_id)
        if not subtask:
            raise TaskException(TaskMessage.SUBTASK_NOT_FOUND, TaskStatusCode.SUBTASK_NOT_FOUND)
        task = await self.task_repository.get_work_item_by_id(subtask.parent)
        if task:
            if not task.assigned_id or user_id not in task.assigned_id:
                raise TaskException(TaskMessage.TASKER_NOT_MATCH_TASK, TaskStatusCode.TASKER_NOT_MATCH_TASK)
        update_task = await self.task_repository.update_work_item(subtask_id,data.model_dump(exclude_unset=True))
        if update_task:
            return ResponseModel(data=TaskResponse.model_validate(update_task))
        raise TaskException(TaskMessage.SUBTASK_NOT_FOUND, TaskStatusCode.SUBTASK_NOT_FOUND)

    async def create_user_task(self, data: CreateUserTaskModel):
        sprint = await self.task_repository.get_work_item_by_id(data.parent)
        if not sprint:
            raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)
        else:
            if sprint.type != WorkItemType.BACKLOG and sprint.type != WorkItemType.STORY:
                raise TaskException(TaskMessage.USER_TASK_PARENT_NOT_MATCH, TaskStatusCode.USER_TASK_PARENT_NOT_MATCH_TYPE)
        task = await self.task_repository.create_work_item(data.model_dump())
        return ResponseModel(data=TaskResponse.model_validate(task))

    async def update_user_task(self, task_id:str, data: UpdateUserTaskModel):
        task = await self.task_repository.get_work_item_by_id(task_id)

        if not task:
            raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
        update_task = await self.task_repository.update_work_item(task_id, data.model_dump(exclude_unset=True))
        if update_task:
            return ResponseModel(data=TaskResponse.model_validate(update_task))
        raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
    async def create_story(self, task_data: CreateStoryModel, handler_id: str):
        if task_data.assigned_id:
            for tasker in task_data.assigned_id:
                await self.user_service.get_user_by_id(tasker)
        # sprint or backlog, if backlog =>
        sprint = await self.task_repository.get_work_item_by_id(task_data.parent)
        if not sprint:
            raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)
        # check sprint/backlog not found
        if not (sprint.type == WorkItemType.BACKLOG and sprint.parent == handler_id):
            await self._check_handler_of_project(sprint.parent, handler_id)
        story = await self.task_repository.create_work_item(task_data.model_dump())
        return ResponseModel(data=TaskResponse.model_validate(story))
    async def update_story(self, story_id: str, task_data: UpdateStoryModel, handler_id: str):
        if task_data.assigned_id:
            for tasker in task_data.assigned_id:
                await self.user_service.get_user_by_id(tasker)
        story = await self.task_repository.get_work_item_by_id(story_id)
        if not story:
            raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
        sprint = await self.task_repository.get_work_item_by_id(story.parent)
        if not (sprint.type == WorkItemType.BACKLOG and sprint.parent == handler_id):
            # print("story", sprint)
            await self._check_handler_of_project(sprint.parent, handler_id)
        # check type update !=story => if current story has task inside => raise
        if task_data.type and task_data.type != WorkItemType.STORY:
            # count children
            filters = FilterWorkItemModel(parent=story_id, offset=0, limit=1,type=[WorkItemType.TASK])
            count = await self.task_repository.count_work_item(filters)
            if count > 0:
                raise TaskException(TaskMessage.NOT_CHANGE_TYPE_ITEM_HAS_CHILDREN, TaskStatusCode.NOT_CHANGE_TYPE_ITEM_HAS_CHILDREN)


        updated_story = await self.task_repository.update_work_item(story_id,task_data.model_dump(exclude_unset=True))
        if updated_story:
            return ResponseModel(data=TaskResponse.model_validate(updated_story))
        raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)

    async def _get_task_story(self, response:TaskResponse):
        children =  await self.task_repository.get_children(str(response.id))
        # logger.info('check children: %s', children)
        for child in children:
            logger.info('check child: %s', child)
        response.children =[TaskResponse.model_validate(child)
                            for child in children
                            ]

    async def _check_handler_of_project(self, project_id:str, user_id:str):
        # check case backlog of user-> project_id is user_id -> not check
        if project_id == user_id:
            return
        project = await self.task_repository.get_work_item_by_id(project_id)
        if not project:
            raise ProjectException(ProjectMessage.NOT_FOUND, ProjectStatusCode.NOT_FOUND)
        if not project.handler_id:
            raise ProjectException(ProjectMessage.NOT_HAVE_HANDLER, ProjectStatusCode.NOT_HAVE_HANDLER)
        if user_id not in project.handler_id and user_id not in project.assigned_id:
            raise TaskException(TaskMessage.NOT_HANDLER_PR0JECT, TaskStatusCode.NOT_HANDLER_PR0JECT)

    async def _auto_gen_order(self, filters: FilterOrderModel, filter_item: FilterWorkItemModel)->tuple[list[TaskResponse], int]:
        # check has any order
        logger.info('check gen order')
        filters.offset = filter_item.offset
        filters.limit = filter_item.limit
        total = await self.order_repository.count_orders(filters.model_dump(exclude_unset=True))
        count_task = await self.task_repository.count_work_item(filter_item)
        list_response = []
        logger.info('total order: %s', total)
        logger.info('total task: %s', count_task)
        if total != count_task:
            logger.info('total task not equal total order')
            list_task = await self.task_repository.filter_work_item_for_order(
                filter_item)
            list_order = await self.order_repository.get_all_orders(filters.model_dump(exclude_unset=True))
            # use map to check miss order in case new task
            order_map = {o.object_id: o.order for o in list_order}
            list_new_order = []
            task_map = {}
            # get miss tasks and map
            missing_tasks = []
            for task in list_task:
                if str(task.id) not in order_map:
                    missing_tasks.append(task)
                task_map[str(task.id)]=task
                logger.info('debug task: %s', task)

            missing_tasks = [task for task in list_task if str(task.id) not in order_map]
            current_position = list_order[0].order if total > 0 else None

            for miss_task in missing_tasks:
                lexorank_position = LexorankUtil.get_lexorank_between(current_position, None)
                new_order = CreateOrderModel(object_id=str(miss_task.id), parent_id= miss_task.parent, owner_id= filters.owner_id, type= filter_item.type_order, order= lexorank_position)
                current_position = lexorank_position
                # add new order to list order
                list_order = [new_order] + list_order
                list_new_order.append(new_order.model_dump())

            await self.order_repository.insert_many_orders(list_new_order)
            for order in list_order:
                task_doc = task_map[order.object_id]
                validate_task = TaskResponse.model_validate(task_doc)
                validate_task.order = order.order
                list_response.append(validate_task)
            logger.info('list response with order: %s', list_response)
            list_response[:] = list_response[filter_item.offset:filter_item.offset+ filter_item.limit]
        else:
            # list order ->task
            # use map to sort order task
            list_order, total = await self.order_repository.get_list_orders(filters.model_dump(exclude_unset=True))

            list_task_id = [order.object_id for order in list_order]
            filter_item.list_ids = list_task_id
            list_task, total_task = await self.task_repository.get_list_work_items(filter_item)
            task_map = {str(task.id): task for task in list_task}

            for order in list_order:
                task_doc = task_map[order.object_id]
                validate_task = TaskResponse.model_validate(task_doc)
                validate_task.order = order.order
                list_response.append(validate_task)
            logger.info('list response with order: %s', list_response)
        # check offset, limit
        return list_response, count_task



    async def check_parent_type(self, parent_type):
        pass