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
import asyncio

class TaskService:
    def __init__(self, task_repository: WorkItemRepository, user_service: UserService, project_service: ProjectService):
        self.task_repository = task_repository
        self.user_service = user_service
        self.project_service = project_service

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
        if handler_id:
            task = await self.task_repository.get_work_item_by_id(task_id)
            if not task:
                raise TaskException(TaskMessage.TASK_NOT_FOUND, TaskStatusCode.TASK_NOT_FOUND)
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

        update_task = await self.task_repository.update_work_item(task_id,task_data.model_dump(exclude_unset=True))
        if update_task:
            return ResponseModel(data=TaskResponse.model_validate(update_task))
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

    async def get_list_tasks(self, filters: FilterWorkItemModel):
        list_tasks, total = await self.task_repository.get_list_work_items(filters)
        list_response = []
        for task_item in list_tasks:
            list_response.append(TaskResponse.model_validate(task_item))
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