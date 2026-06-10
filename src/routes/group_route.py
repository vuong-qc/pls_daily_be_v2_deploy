from src.repositories.group.beanie_group_repository import BeanieGroupRepository
from src.services.group_service import GroupService
from src.models.group.request.create_group_model import CreateGroupModel
from src.models.group.request.update_group_model import UpdateGroupModel
from src.models.group.request.filter_group_model import FilterGroupModel
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.enums.user_role_enum import UserRole
from src.utils.role_checker_util import RoleCheckerUtil
from src.utils.proxy_util import get_current_user_by_token

router = APIRouter(
    tags=["Group"],
)

def get_group_service() -> GroupService:
    group_repo = BeanieGroupRepository()
    return GroupService(group_repo)

@router.post("/create-group",
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             # dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value]))]
            )
async def create_group(req: CreateGroupModel,
                       user_data: dict = Depends(get_current_user_by_token),
                       service: GroupService = Depends(get_group_service)
                       ):
    user_id = user_data.get('sub')
    req.created_by = user_id
    return await service.create_group(req)

@router.put("/update-group/{group_id}",
            status_code=status.HTTP_202_ACCEPTED,
            response_model=ResponseModel,
            dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value]))]
            )
async def update_group(group_id:str,
                       req: UpdateGroupModel,
                       user_data: dict = Depends(get_current_user_by_token),
                       service: GroupService = Depends(get_group_service)
                       ):
    return await service.update_group(group_id, req)
@router.delete("/delete-group/{group_id}",
                dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value]))],
               status_code=status.HTTP_204_NO_CONTENT,)
async def delete_group(group_id:str,
                       user_data: dict = Depends(get_current_user_by_token),
                       service: GroupService = Depends(get_group_service)
                       ):
    return await service.delete_group(group_id)

@router.get("/list-groups",
            status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel,
            )
async def get_list_groups(
        query: Annotated[FilterGroupModel, Query()],
        service: GroupService = Depends(get_group_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await service.get_list_group(query)