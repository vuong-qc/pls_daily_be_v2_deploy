from typing import Optional
from beanie import PydanticObjectId

from src.enums.session_status_enum import SessionStatusEnum
from src.models.session.request.filter_session_model import FilterSessionModel
from src.models.task.request.create_task_model import CreateTaskModel, CreateUserTaskModel, CreateStoryModel
from src.models.task.request.update_task_model import UpdateTaskModel, UpdateUserTaskModel, UpdateStoryModel
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.services.user_service import UserService
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.services.project_service import ProjectService
from src.exception.task_exception import TaskException, TaskMessage, TaskStatusCode
from src.models.task.response.task_response_model import TaskResponse, ResponseSprintStatisticTask, ResponseCountTaskPoint
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
from src.repositories.session.session_repository import SessionRepository
import asyncio
import logging
from src.enums.task_status_enum import TaskStatusEnum, TaskPreviewStatusEnum
from src.enums.work_item_type import WorkItemType
from src.utils.datetime_util import DateTimeUtil
logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, task_repository: WorkItemRepository, user_service: UserService,
                 project_service: ProjectService, order_repository: OrderRepository, session_repository: SessionRepository, ):
        self.task_repository = task_repository
        self.user_service = user_service
        self.project_service = project_service
        self.order_repository = order_repository
        self.session_repository = session_repository

    async def create_task(self, task_data: CreateTaskModel, handler_id:str = None):
        task_data.owner_id = handler_id
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
        response = TaskResponse.model_validate(task)
        if task_data.order_type:

            order_data = CreateOrderModel(parent_id=task_data.parent, owner_id=handler_id, type=task_data.order_type, object_id=str(response.id), order='')
            order_model = await self.order_repository.create_order(order_data.model_dump(), task_data.prev_order, task_data.next_order)
            response.order = order_model.order
        else:
            filter_order = FilterOrderModel(parent_id=task.parent, owner_id=handler_id,
                                            object_id=str(task.id))
            order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))
            response.order = order_model.order if order_model else order_model
        return ResponseModel(data=response)

    async def update_task(self, task_id:str, task_data: UpdateTaskModel, handler_id:str = None):
        if task_data.assigned_id:
            for tasker in task_data.assigned_id:
                await self.user_service.get_user_by_id(tasker)

        task = await self.task_repository.get_work_item_by_id(task_id)
        if not task:
            raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
        if task_data.assigned_id and (task.des is None and task.point is None and task.point is None and task.deadline is None):
            raise TaskException(TaskMessage.CANT_ASSIGN_TASK, TaskStatusCode.CANT_ASSIGN_TASK)
        if not PydanticObjectId.is_valid(task_data.parent):
            raise TaskException(TaskMessage.PARENT_TASK_NOT_FOUND, TaskStatusCode.PARENT_TASK_NOT_FOUND)
        if handler_id:
            # if user_id not in user assign => check role
            if handler_id not in task.assigned_id:
                sprint = await self.task_repository.get_work_item_by_id(task.parent)
                if sprint.type == WorkItemType.SPRINT or sprint.type == WorkItemType.BACKLOG:
                    logger.info("update task in case sprint backlog")
                    await self._check_handler_of_project(sprint.parent, handler_id)
                # case story
                if sprint.type == WorkItemType.STORY:
                    # get sprint/backlog
                    # check param type exist => raise error
                    logger.info("update task in case story")
                    if task_data.type and task_data.type != WorkItemType.TASK:
                        raise TaskException(TaskMessage.NOT_UPDATE_TASK_TYPE_IN_STORY, TaskStatusCode.NOT_UPDATE_TASK_TYPE_IN_STORY)
                    parent = await self.task_repository.get_work_item_by_id(sprint.parent)
                    if parent:
                        await self._check_handler_of_project(parent.parent, handler_id)
        # check task has subtask, if update type != task => raise error
        if task_data.type and task_data.type != WorkItemType.TASK:
            # count children
            filters = FilterWorkItemModel(parent=task_id, offset=0, limit=1,type=[WorkItemType.SUBTASK, WorkItemType.TASK])
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
                logger.info("check filter order: %s", filter_order)
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
            # elif sprint.type == WorkItemType.BACKLOG:
            #     if sprint.parent != handler_id:
            #         raise TaskException(TaskMessage.NOT_HANDLER_PR0JECT, TaskStatusCode.NOT_HANDLER_PR0JECT)
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
        list_response = []
        if filters.is_today:
            # query in session
            start_of_today_vn = DateTimeUtil.get_start_time_today()
            logger.info(f"start_of_today_vn: %s{start_of_today_vn}")
            filters_session = FilterSessionModel(start_time=start_of_today_vn,status= [SessionStatusEnum.NEW, SessionStatusEnum.IN_PROGRESS],limit=1, offset=0, user_id=user_id)
            list_session, total = await self.session_repository.get_list_session(filters_session)
            print(list_session)
            print(total)
            if total < 1:
                return ResponsePaginatedModel(data=[], total=total, offset= filters.offset)
            list_task_today = list_session[0].list_task
            filters.list_ids = list_task_today
            print(filters)
            list_tasks, total = await self.task_repository.get_list_work_items(filters)
            print("task",list_tasks)
            print("total",total)
            for task in list_tasks:
                list_response.append(TaskResponse.model_validate(task))
            if filters.type and (WorkItemType.STORY in filters.type or WorkItemType.BACKLOG in filters.type):
                await asyncio.gather(*[
                    self._get_task_story(
                        task, FilterOrderModel(type=filters.type_order, owner_id=user_id, parent_id=str(task.id)),
                        FilterWorkItemModel(offset=0, limit=100, parent=str(task.id), type_order=filters.type_order,
                                            deadline_start=filters.deadline_start, deadline_end=filters.deadline_end,
                                            status=filters.status,
                                            assigned_id=filters.assigned_id),
                    )
                    for task in list_response
                ])
            self._handler_inject_task_to_story(list_response)
            total = await self._count_task(filters, total)
            return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

        # case task
        if filters.type_order:
            # handle case story fetched with its task
            # list_response, total = await self._auto_gen_order(filter_order, filters)
            list_response, total = await LexorankUtil.auto_gen_order(filter_order, filters, TaskResponse, self.task_repository, self.order_repository)
            logger.info(f"list_response len: {len(list_response)}")
            for task in list_response:
                logger.info("check print task later %s, %s", task.title, task.type)
        else:
            list_tasks, total = await self.task_repository.get_list_work_items(filters)
            for task in list_tasks:
                list_response.append(TaskResponse.model_validate(task))
        self._handler_inject_task_to_story(list_response)

        if filters.type and (WorkItemType.STORY in filters.type  or WorkItemType.BACKLOG in filters.type):
            await asyncio.gather(*[
                self._get_task_story(
                    task, FilterOrderModel(type=filters.type_order, owner_id=user_id, parent_id=str(task.id)), FilterWorkItemModel(offset=0, limit=100, parent=str(task.id),
                                                                                                                                   status=filters.status,
                                                                                                                                   deadline_start=filters.deadline_start,
                                                                                                                                   deadline_end=filters.deadline_end,
                                                                                                                                   type_order=filters.type_order, assigned_id=filters.assigned_id),
                )
                for task in list_response
            ])
        logger.info(f"list_response later len: {len(list_response)}")
        for task in list_response:
            logger.info("check print task later %s, %s", task.title, task.type)
        total = await self._count_task(filters, total)
        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

    async def create_subtask(self, data: CreateSubtaskModel, user_id: str):
        # check user is assigned to task to create subtask
        task = await self.task_repository.get_work_item_by_id(data.parent)
        if task:
            if task.status == TaskStatusEnum.CANCELED:
                raise TaskException(TaskMessage.CANCELED_TASK, TaskStatusCode.CANCELED_TASK)
            if not task.assigned_id or user_id not in task.assigned_id:
                raise TaskException(TaskMessage.TASKER_NOT_MATCH_TASK, TaskStatusCode.TASKER_NOT_MATCH_TASK)

            if task.status == TaskStatusEnum.NEW or task.status == TaskStatusEnum.DONE:
                # update task status is In processing
                update_data = UpdateTaskModel(status=TaskStatusEnum.PROCESSING)
                await self.task_repository.update_work_item(data.parent, update_data.model_dump(exclude_unset=True))

        subtask = await self.task_repository.create_work_item(data.model_dump())
        return ResponseModel(data=TaskResponse.model_validate(subtask))

    async def update_subtask(self, subtask_id:str, data: UpdateSubtaskModel, user_id: str):
        subtask = await self.task_repository.get_work_item_by_id(subtask_id)
        if data.status != TaskStatusEnum.DONE:
            data.session_id = None

        if not subtask:
            raise TaskException(TaskMessage.SUBTASK_NOT_FOUND, TaskStatusCode.SUBTASK_NOT_FOUND)
        task = await self.task_repository.get_work_item_by_id(subtask.parent)
        if task:
            if not task.assigned_id or user_id not in task.assigned_id:
                raise TaskException(TaskMessage.TASKER_NOT_MATCH_TASK, TaskStatusCode.TASKER_NOT_MATCH_TASK)
        update_task = await self.task_repository.update_work_item(subtask_id,data.model_dump(exclude_unset=True))
        if update_task:
            # update task when session
            if data.status == TaskStatusEnum.DONE and data.session_id:
                await self._handle_update_status_task_done(update_task.parent, data.session_id)
            if data.status == TaskStatusEnum.PROCESSING and task.status == TaskStatusEnum.DONE:
                await self.task_repository.update_work_item(subtask.parent,{"session_id": None, "status": TaskStatusEnum.PROCESSING})
            return ResponseModel(data=TaskResponse.model_validate(update_task))
        raise TaskException(TaskMessage.SUBTASK_NOT_FOUND, TaskStatusCode.SUBTASK_NOT_FOUND)

    async def create_user_task(self, task_data: CreateUserTaskModel, user_id:str):
        task_data.owner_id = user_id
        sprint = await self.task_repository.get_work_item_by_id(task_data.parent)
        if not sprint:
            raise SprintException(SprintMessage.NOT_FOUND, SprintStatusCode.NOT_FOUND)
        else:
            if sprint.type != WorkItemType.BACKLOG and sprint.type != WorkItemType.STORY:
                raise TaskException(TaskMessage.USER_TASK_PARENT_NOT_MATCH, TaskStatusCode.USER_TASK_PARENT_NOT_MATCH_TYPE)
        task = await self.task_repository.create_work_item(task_data.model_dump())
        response = TaskResponse.model_validate(task)
        if task_data.order_type:
            order_data = CreateOrderModel(parent_id=task_data.parent, owner_id=user_id, type=task_data.order_type,
                                          object_id=str(response.id), order='')
            order_model = await self.order_repository.create_order(order_data.model_dump(), task_data.prev_order,
                                                                   task_data.next_order)
            response.order = order_model.order
        else:
            filter_order = FilterOrderModel(parent_id=task.parent, owner_id=user_id,
                                            object_id=str(task.id))
            order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))
            response.order = order_model.order if order_model else order_model
        return ResponseModel(data=response)

    async def update_user_task(self, task_id:str, task_data: UpdateUserTaskModel, user_id:str):
        task = await self.task_repository.get_work_item_by_id(task_id)

        if not task:
            raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
        update_task = await self.task_repository.update_work_item(task_id, task_data.model_dump(exclude_unset=True))
        if update_task:
            response = TaskResponse.model_validate(update_task)

            if task_data.order_type:
                filter_order = FilterOrderModel(parent_id=task.parent, owner_id=user_id, type=task_data.order_type,
                                                object_id=task_id)
                order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))

                if not order_model:
                    raise

                parent_id = task_data.parent if task_data.parent else task.parent
                update_data_order = UpdateOrderModel(type=task_data.order_type, parent_id=parent_id)
                updated_order = await self.order_repository.update_order(str(order_model.id),
                                                                         update_data_order.model_dump(
                                                                             exclude_unset=True),
                                                                         task_data.prev_order, task_data.next_order)
                response.order = updated_order.order if updated_order else updated_order
            else:
                filter_order = FilterOrderModel(parent_id=task.parent, owner_id=user_id,
                                                object_id=task_id)
                order_model = await self.order_repository.find_one_order(filter_order.model_dump(exclude_unset=True))
                response.order = order_model.order if order_model else order_model

            return ResponseModel(data=response)
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
        response = TaskResponse.model_validate(story)
        if task_data.order_type:
            order_data = CreateOrderModel(parent_id=task_data.parent, owner_id=handler_id, type=task_data.order_type,
                                          object_id=str(response.id), order='')
            order_model = await self.order_repository.create_order(order_data.model_dump(), task_data.prev_order,
                                                                   task_data.next_order)
            response.order = order_model.order
        return ResponseModel(data=response)
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
            # add list task to story
            response = TaskResponse.model_validate(updated_story)
            await self._get_task_story(response)
            return ResponseModel(data=response)
        raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)

    async def _get_task_story(self, response:TaskResponse, filter_order: Optional[FilterOrderModel] = None, filter_item: Optional[FilterWorkItemModel] = None):
        if (response.children is None or len(response.children) == 0) and response.type in [WorkItemType.BACKLOG, WorkItemType.STORY]:
            # children =  await self.task_repository.get_children(str(response.id))
            # # logger.info('check children: %s', children)
            # for child in children:
            #     logger.info('check child: %s', child)
            # response.children =[TaskResponse.model_validate(child)
            #                     for child in children
            #                     ]
            if filter_order and filter_item and filter_item.type_order:
                logger.info(f"filter_order: {filter_order}, filter_item: {filter_item}")
                list_response, total = await LexorankUtil.auto_gen_order(filter_order, filter_item, TaskResponse, self.task_repository, self.order_repository)
                response.children = list_response
                return
            children = await self.task_repository.get_children(parent_id=str(response.id))
            logger.info('check children len: %s', len(children))
            for child in children:
                logger.info('check child: %s', child)
            response.children =[TaskResponse.model_validate(child)
                                for child in children
                                ]


    async def _check_handler_of_project(self, project_id:str, user_id:str):
        if user_id == project_id:
            # case backlog
            return
        project = await self.task_repository.get_work_item_by_id(project_id)
        if not project:
            raise ProjectException(ProjectMessage.NOT_FOUND, ProjectStatusCode.NOT_FOUND)
        if not project.handler_id:
            raise ProjectException(ProjectMessage.NOT_HAVE_HANDLER, ProjectStatusCode.NOT_HAVE_HANDLER)
        if user_id not in project.handler_id and user_id not in project.assigned_id:
            raise TaskException(TaskMessage.NOT_HANDLER_PR0JECT, TaskStatusCode.NOT_HANDLER_PR0JECT)

    async def auto_update_late_dl_task(self):
        filters = FilterWorkItemModel(offset=0, limit=1, deadline_end=DateTimeUtil.current_milli_time(),
                                      type=[WorkItemType.TASK], status=[TaskStatusEnum.NEW, TaskStatusEnum.PROCESSING])
        list_task = await self.task_repository.filter_work_item_for_order(filters)
        list_ids = [str(task.id) for task in list_task]
        update_data = UpdateTaskModel(review_status=TaskPreviewStatusEnum.LATE)
        if list_ids:
            logger.info('list ids: %s', list_ids)
            logger.info('list task: %s', list_task)
            await self.task_repository.update_many(list_ids, update_data.model_dump(exclude_unset=True))


    def _handler_inject_task_to_story(self, list_response: list):
        parent_map = dict()
        for response in list_response:
            # add if has parent is story
            # logger.debug("response: %s", response.title)
            if response.parent_model and response.parent_model.type == WorkItemType.STORY:
                parent_id = response.parent
                logging.info("case task in story: %s", response.title)
                if parent_id not in parent_map:
                    parent_obj = TaskResponse.model_validate(response.parent_model.model_dump())
                    parent_obj.children = []
                    parent_map[parent_id] = parent_obj
                    logging.info("create case task of story: %s", response.parent_model.title)

                parent_map[parent_id].children.append(response)
            elif response.type == WorkItemType.STORY:
                logger.info('case story: %s', response.title)
                # parent_map[response.id] = response
                if response.parent not in parent_map:
                    response.children = []
                    parent_map[str(response.id)] = response
                    logger.info("case story: %s", response.title)
            else:
                logging.info("case task sprint: %s", response.title)
                parent_map[str(response.id)] = response
        all_parents = list(parent_map.values())

        list_response[:] = all_parents

    async def get_tasks_by_sprint(self, sprint_id:str, user_id:str):
        task_story_of_sprint = await self.task_repository.get_children(parent_id=sprint_id, user_id=user_id)
        list_story_ids = []
        list_tasks = []
        list_task_id = []
        print("task of sprint",task_story_of_sprint)
        for item in task_story_of_sprint:
            if item.type == WorkItemType.STORY:
                list_story_ids.append(str(item.id))
            elif item.type == WorkItemType.TASK:
                list_tasks.append(item)
                list_task_id.append(str(item.id))
        print("list_story_ids:", list_story_ids)
        print("list_tasks:", list_tasks)
        print("list_task_id:", list_task_id)
        # get task of story
        task_by_story = await self.task_repository.get_children_by_parents(list_story_ids)
        for task in task_by_story:
            list_tasks.append(task)
            list_task_id.append(str(task.id))

        task_with_count_status = await self.task_repository.count_items_by_parent_status(list_task_id, [TaskStatusEnum.NEW.value, TaskStatusEnum.PROCESSING.value, TaskStatusEnum.LATE.value, TaskStatusEnum.DONE.value])
        print("test",task_with_count_status)

        total_done_tasks = 0
        total_point_done_tasks = 0
        list_response = []
        total_point = 0

        for task in list_tasks:
            status_count_object = task_with_count_status.get(str(task.id))
            if status_count_object:
                count_new = status_count_object.get(TaskStatusEnum.NEW.value,0)
                count_processing = status_count_object.get(TaskStatusEnum.PROCESSING.value, 0)
                count_done = status_count_object.get(TaskStatusEnum.DONE.value, 0)
                response = TaskResponse.model_validate(task)
                total_subtask = count_done + count_processing  + count_new
                response.percent_process = count_done / total_subtask if total_subtask > 0 else 0
                if task.status == TaskStatusEnum.DONE.value:
                    total_done_tasks += 1
                    total_point_done_tasks += task.point
                total_point += task.point
                list_response.append(response)
        return ResponseSprintStatisticTask(data=list_response, total=len(list_response), total_point=total_point, total_point_done_tasks=total_point_done_tasks, total_done_tasks=total_done_tasks,offset=0)

    async def count_my_tasks(self, user_id:str):
        filters = FilterWorkItemModel(limit=1, offset=0, assigned_id=[user_id], type=[WorkItemType.TASK], status=[status for status in TaskStatusEnum if status!= TaskStatusEnum.CANCELED])
        count_my_tasks = await self.task_repository.count_work_item(filters)
        count_total_point = await self.task_repository.count_point(filters)


        filters.status = [status for status in TaskStatusEnum if status!= TaskStatusEnum.CANCELED and status!= TaskStatusEnum.DONE]
        count_not_done_tasks = await self.task_repository.count_work_item(filters)
        count_not_done_point = await self.task_repository.count_point(filters)

        response = ResponseCountTaskPoint(count_my_tasks=count_my_tasks,count_total_point=count_total_point,count_not_done_tasks= count_not_done_tasks, count_not_done_point=count_not_done_point)

        return ResponseModel(data=response)

    async def copy_task(self, task_id: str):
        task = await self.task_repository.get_work_item_by_id(task_id)
        if not task:
            raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)

        cp_task = CreateTaskModel(**task.model_dump())
        cp_task.assigned_id = None

        new_task = await self.task_repository.create_work_item(cp_task.model_dump())
        response = TaskResponse.model_validate(new_task)
        return ResponseModel(data=response)

    async def _handle_update_status_task_done(self,task: str, session_id: str):
        # count subtask done/ total =process_percent
        filter_subtask_done = FilterWorkItemModel(status=[TaskStatusEnum.DONE], parent=str(task), offset=0, limit=1)
        count_sub_task_done = await self.task_repository.count_work_item(filter_subtask_done)

        filter_all_subtask = FilterWorkItemModel(status=[TaskStatusEnum.NEW, TaskStatusEnum.PROCESSING],
                                                 parent=str(task), offset=0, limit=1)
        count_total_subtask = await self.task_repository.count_work_item(filter_all_subtask) + count_sub_task_done
        logger.info(f"count_sub_task_done: %s{count_sub_task_done}")
        logger.info(f"count_total_subtask: %s{count_total_subtask}")
        if count_total_subtask == count_sub_task_done and count_sub_task_done > 0:
            update_data = UpdateTaskModel(status=TaskStatusEnum.DONE, session_id=session_id)
            task_data =await self.task_repository.update_work_item(task, update_data.model_dump(
                exclude_unset=True))
            if not task_data:
                raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
            await self._handle_update_sprint_done(task_data.parent)

    async def _handle_update_sprint_done(self, sprint_id: str):
        filter_task_done = FilterWorkItemModel(status=[TaskStatusEnum.DONE], parent=str(sprint_id), offset=0, limit=1)
        count_task_done = await self.task_repository.count_work_item(filter_task_done)

        filter_all_subtask = FilterWorkItemModel(status=[TaskStatusEnum.NEW, TaskStatusEnum.PROCESSING],
                                                 parent=str(sprint_id), offset=0, limit=1)
        count_total_task = await self.task_repository.count_work_item(filter_all_subtask) + count_task_done
        if count_total_task == count_task_done and count_task_done > 0:
            update_data = UpdateTaskModel(status=TaskStatusEnum.DONE)
            await self.task_repository.update_work_item(sprint_id, update_data.model_dump(
                exclude_unset=True))


    async def _count_task(self, filters: FilterTaskModel, total: int):
        # count = 0
        # if filters.parent:
        #     children = await self.task_repository.get_children(filters.parent)
        #     list_story_ids = []
        #     for child in children:
        #         # print("child", child.type)
        #         if child.type == WorkItemType.TASK:
        #             count += 1
        #         elif child.type == WorkItemType.STORY:
        #             list_story_ids.append(str(child.id))
        #
        #     print("count", count)
        #     print("story_ids", list_story_ids)
        #     story_children = await self.task_repository.get_children_by_parents(list_story_ids, filters.status, filters.assigned_id)
        #     return len(story_children) + count
        #
        # return total
        if (filters.type and WorkItemType.SUBTASK in filters.type) or not filters.parent:
            return total
        return await self.task_repository.count_total_tasks_in_sprint(filters)

    async def statistic_task_summary(self, filters: FilterTaskModel):
        filters.type = [WorkItemType.TASK.value]
        filter_total_task = filters.model_copy(deep=True)
        filter_total_task.status = None

        filter_done_task = filters.model_copy(deep=True)
        filter_done_task.status = [TaskStatusEnum.DONE.value]
        total_task = await self.task_repository.count_by_time_buckets(filter_total_task, True)
        total_done_tasks = await self.task_repository.count_by_time_buckets(filter_done_task)
        total_point = await self.task_repository.sum_point_by_time_buckets(filter_total_task, True)
        total_done_point = await self.task_repository.sum_point_by_time_buckets(filter_done_task)
        response = {}
        response["total_point"] = total_point
        response["total_done_point"] = total_done_point
        response["total_tasks"] = total_task
        response["total_done_tasks"] = total_done_tasks
        return ResponseModel(data=response)
