from src.models.response_model import ResponseModel, ResponsePaginatedModel
from typing import Annotated
from src.models.sprint.request.create_sprint_model import CreateSprintModel
from src.models.sprint.request.update_sprint_model import UpdateSprintModel
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.services.project_service import ProjectService
from src.services.user_service import UserService
from src.routes.project_route import get_project_service
from src.routes.user_route import get_user_service
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from fastapi import Depends, APIRouter, Query, status
from src.services.sprint_service import SprintService
from src.utils.role_checker_util import RoleCheckerUtil
from src.enums.user_role_enum import UserRole
from src.utils.proxy_util import get_current_user_by_token

router = APIRouter(
    tags=['sprint'],
)

def get_sprint_service(
        user_service: UserService = Depends(get_user_service),
        project_service: ProjectService = Depends(get_project_service),
):
    sprint_repo = BeanieWorkItemRepository()
    return SprintService(sprint_repo, user_service, project_service)

@router.post('/create-sprint',
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             dependencies=[Depends(RoleCheckerUtil([UserRole.HANDLER.value]))]
)
async def create_sprint(
        req: CreateSprintModel,
        sprint_service: SprintService = Depends(get_sprint_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get('sub')
    return await sprint_service.create_sprint(req, user_id)

@router.put('/update-sprint/{sprint_id}',
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            dependencies=[Depends(RoleCheckerUtil([UserRole.HANDLER.value]))]
            )
async def update_sprint(
        sprint_id: str,
        update_data: UpdateSprintModel,
        sprint_service: SprintService = Depends(get_sprint_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get('sub')
    return await sprint_service.update_sprint(sprint_id, update_data, user_id)
@router.delete('/delete-sprint/{sprint_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RoleCheckerUtil([UserRole.HANDLER.value]))]
               )
async def delete_sprint(
        sprint_id: str,
        sprint_service: SprintService = Depends(get_sprint_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get('sub')
    return await sprint_service.delete_sprint(sprint_id, user_id)

@router.get('/get-list-sprints',
            status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel,
            )
async def get_list_sprints(
        query: Annotated[FilterWorkItemModel, Query()],
        sprint_service: SprintService = Depends(get_sprint_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await sprint_service.get_list_sprints(query)
