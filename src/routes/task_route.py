from typing import Annotated


from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.subtask.request.create_subtask_model import CreateSubtaskModel
from src.models.subtask.request.update_subtask_model import UpdateSubtaskModel
from src.models.task.request.create_task_model import CreateTaskModel, CreateUserTaskModel, CreateStoryModel
from src.models.task.request.update_task_model import UpdateTaskModel, UpdateUserTaskModel, UpdateStoryModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from fastapi import APIRouter, Query, Depends, status
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.services.task_service import TaskService
from src.utils.role_checker_util import RoleCheckerUtil
from src.enums.user_role_enum import UserRole
from src.utils.proxy_util import get_current_user_by_token
from src.services.project_service import ProjectService
from src.services.user_service import UserService
from src.routes.project_route import get_project_service
from src.routes.user_route import get_user_service
router = APIRouter(
    tags=["task"]
)

def get_task_service(
    project_service: ProjectService = Depends(get_project_service),
    user_service: UserService = Depends(get_user_service),
):
    task_repo = BeanieWorkItemRepository()
    return TaskService(task_repo, user_service, project_service)
@router.post('/create-story',
            status_code=status.HTTP_201_CREATED,
             summary='Story create in backlog/project',
             response_model=ResponseModel,
             )
async def create_story(
        req: CreateStoryModel,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.create_story(req, user_id)

@router.put('/update-story/{story_id}',
            status_code=status.HTTP_202_ACCEPTED,
            summary='Story update in backlog/project',
            response_model=ResponseModel,
            )
async def update_story(
        story_id: str,
        data: UpdateStoryModel,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.update_story(story_id, data, user_id)

@router.post("/create_task",
            summary='Handler create task of project',
            status_code=status.HTTP_201_CREATED,
            response_model=ResponseModel,
            dependencies=[Depends(RoleCheckerUtil([UserRole.HANDLER.value]))]
)
async def create_task(
        req: CreateTaskModel,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.create_task(req, user_id)

@router.put("/update_task/{task_id}",
            summary='Handler update task of project',
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            dependencies=[Depends(RoleCheckerUtil([UserRole.HANDLER.value]))]
)
async def update_task(
        task_id: str,
        req: UpdateTaskModel,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.update_task(task_id, req, user_id)

@router.get("/get-list-task",
            status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel,
            summary="Get task list with filter",
)
async def get_list_task(
        query: Annotated[FilterWorkItemModel, Query()],
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await task_service.get_list_tasks(query)

@router.delete("/delete-task/{task_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RoleCheckerUtil([UserRole.HANDLER.value]))],
               summary="Handler delete task of project",
               )
async def delete_task(
        task_id: str,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.delete_task(task_id, user_id)

@router.post('/create-user-task',
            status_code=status.HTTP_201_CREATED,
             summary='User create personal task in backlog',
             response_model=ResponseModel
             )
async def create_user_task(
        req: CreateUserTaskModel,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await task_service.create_user_task(req)


@router.put('/update-user-task/{task_id}',
            status_code=status.HTTP_202_ACCEPTED,
            summary='User update personal task in backlog',
            )
async def update_user_task(
        task_id: str,
        data: UpdateUserTaskModel,
        task_service: TaskService = Depends(get_task_service),
):
    return await task_service.update_user_task(task_id, data)

@router.post('/create-subtask',
            status_code=status.HTTP_201_CREATED,
             summary='Tasker create subtask of task',
             response_model=ResponseModel,
             )
async def create_subtask(
        req: CreateSubtaskModel,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.create_subtask(req, user_id)

@router.put('/update-subtask/{task_id}',
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            summary='Tasker update subtask of task',
            )
async def update_subtask(
        task_id: str,
        data: UpdateSubtaskModel,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.update_subtask(task_id, data, user_id)



