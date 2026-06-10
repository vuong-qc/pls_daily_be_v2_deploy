from typing import Annotated

from fastapi import APIRouter, Query, Depends, status
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.services.project_service import ProjectService
from src.services.group_service import GroupService
from src.services.user_service import UserService
from src.routes.user_route import get_user_service
from src.routes.group_route import get_group_service
from src.enums.user_role_enum import UserRole
from src.models.project.request.create_project_model import CreateProjectModel
from src.models.project.request.update_project_model import UpdateProjectModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.utils.proxy_util import get_current_user_by_token
from src.utils.role_checker_util import RoleCheckerUtil
from src.models.response_model import ResponseModel, ResponsePaginatedModel

router = APIRouter(
    tags=["project"],
)

def get_project_service(
        user_service: UserService = Depends(get_user_service),
        group_service: GroupService = Depends(get_group_service),
):
    project_repo = BeanieWorkItemRepository()
    return ProjectService(project_repo, user_service, group_service)

@router.post("/create_project",
             status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value, UserRole.ADMIN.value]))],
             response_model=ResponseModel
             )
async def create_project(
        req: CreateProjectModel,
        project_service: ProjectService = Depends(get_project_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data.get("sub")
    req.owner_id = user_id
    return await project_service.create_project(req)

@router.get("/get-list_project",
            status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel
            )
async def get_list_project(
        query: Annotated[FilterWorkItemModel, Query()],
        project_service: ProjectService = Depends(get_project_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await project_service.get_list_projects(query)

@router.put("/update-project/{project_id}",
            status_code=status.HTTP_202_ACCEPTED,
            response_model=ResponseModel,
            dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value, UserRole.ADMIN.value]))],
            )
async def update_project(
        project_id: str,
        req: UpdateProjectModel,
        project_service: ProjectService = Depends(get_project_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await project_service.update_project(project_id, req)

@router.delete("/delete-project/{project_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value, UserRole.ADMIN.value]))],
               )
async def delete_project(
        project_id: str,
        project_service: ProjectService = Depends(get_project_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await project_service.delete_project(project_id)
