from fastapi import APIRouter, Depends, Query, status

from src.models.user.filter_user_model import FilterUserModel
from src.models.user.update_user_model import UpdateUserModel
from src.repositories.users.beanie_user_repository import BeanieUserRepository
from src.services.user_service import UserService
from src.models.user.create_user_model import CreateUserModel
from src.utils.role_checker_util import RoleCheckerUtil
from src.enums.user_role_enum import UserRole
from src.utils.proxy_util import get_current_user_by_token
from typing import Annotated

router = APIRouter(
    tags=["users"]
)

def get_user_service():
    user_repo = BeanieUserRepository()
    return UserService(user_repo)

@router.post("/create-user",
             status_code=status.HTTP_201_CREATED,
             summary="create new user",
             description="create new user by master",
             dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value, UserRole.ADMIN.value]))],
             )
async def create_user(
        create_user_model: CreateUserModel,
        user_service: UserService = Depends(get_user_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    roles = user_data.get("roles")
    return await user_service.create_user(create_user_model, roles)

@router.get("/get-user/{user_id}",
            summary="get users",
            description="get users by id", )
async def get_user(
        user_id: str,
        user_service: UserService = Depends(get_user_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await user_service.get_user_by_id(user_id)

@router.get("/get-list-user",
            summary="get users list",
            description="get users list",
            )
async def get_list_user(
        filters: Annotated[FilterUserModel, Query()],
        user_service: UserService = Depends(get_user_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await user_service.get_list_user(filters)

@router.put("/update-user/{user_id}",
            summary="update users",
            description="update users by id",
            dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value, UserRole.ADMIN.value]))],

            )
async def update_user(
        user_id: str,
        update_user_model: UpdateUserModel,
        user_service: UserService = Depends(get_user_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    roles = user_data.get("roles")
    return await user_service.update_user(user_id, update_user_model, roles)

@router.get("/get-user-by-email")
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service),
    user_data: dict = Depends(get_current_user_by_token)
):
    return await user_service.get_user_by_email(email)