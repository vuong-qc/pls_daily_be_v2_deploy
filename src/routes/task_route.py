from typing import Annotated

from src.configs import settings
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.subtask.request.create_subtask_model import CreateSubtaskModel
from src.models.subtask.request.update_subtask_model import UpdateSubtaskModel
from src.models.task.request.create_task_model import CreateTaskModel, CreateUserTaskModel, CreateStoryModel
from src.models.task.request.filter_task_model import FilterTaskModel
from src.models.task.request.update_task_model import UpdateTaskModel, UpdateUserTaskModel, UpdateStoryModel
from fastapi import APIRouter, Query, Depends, status, Header, HTTPException
from src.repositories.session.beanie_session_repository import BeanieSessionRepository
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.services.task_service import TaskService
from src.utils.role_checker_util import RoleCheckerUtil
from src.enums.user_role_enum import UserRole
from src.utils.proxy_util import get_current_user_by_token
from src.services.project_service import ProjectService
from src.services.user_service import UserService
from src.routes.project_route import get_project_service
from src.routes.user_route import get_user_service
from src.repositories.order.beanie_order_repository import BeanieOrderRepository
router = APIRouter(
    tags=["task"]
)

def get_task_service(
    project_service: ProjectService = Depends(get_project_service),
    user_service: UserService = Depends(get_user_service),
):
    task_repo = BeanieWorkItemRepository()
    order_repo = BeanieOrderRepository()
    session_repo = BeanieSessionRepository()
    return TaskService(task_repo, user_service, project_service, order_repo, session_repo)
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
        query: Annotated[FilterTaskModel, Query()],
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.get_list_tasks(query, user_id)

@router.get("/get-task/{task_id}",
            status_code=status.HTTP_200_OK,
            summary="Get task details",
            )
async def get_task(
        task_id: str,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await task_service.get_task_by_id(task_id)

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
    user_id = user_data.get("sub")
    return await task_service.create_user_task(req, user_id)


@router.put('/update-user-task/{task_id}',
            status_code=status.HTTP_202_ACCEPTED,
            summary='User update personal task in backlog',
            )
async def update_user_task(
        task_id: str,
        data: UpdateUserTaskModel,
        user_data: dict = Depends(get_current_user_by_token),
        task_service: TaskService = Depends(get_task_service),
):
    user_id = user_data.get('sub')
    return await task_service.update_user_task(task_id, data, user_id)

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

@router.post(f'/{settings.SUB_DOMAIN_AUTO_UPDATE_TASK}',
            status_code=status.HTTP_202_ACCEPTED, )
async def auto_update_status_task(
        x_internal_key: str = Header(),
        task_service: TaskService = Depends(get_task_service),
):
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,)
    return await task_service.auto_update_late_dl_task()

@router.get('/statistics-task-by-sprint/{sprint_id}',
            status_code=status.HTTP_200_OK,
            )
async def statistics_task_by_sprint_id(
        sprint_id: str,
        user_id: str,
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await task_service.get_tasks_by_sprint(sprint_id, user_id)

@router.get('/statistics-my-tasks',
            status_code=status.HTTP_200_OK,
            description='Get total number of tasks, task not done, total point, point not done',
            )
async def statistics_my_tasks(
        task_service: TaskService = Depends(get_task_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    return await task_service.count_my_tasks(user_id)