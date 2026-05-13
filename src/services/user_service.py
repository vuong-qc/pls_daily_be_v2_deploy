from src.models.user.filter_user_model import FilterUserModel
from src.models.user.update_user_model import UpdateUserModel
from src.repositories.users.user_repository import UserRepository
from src.models.user.create_user_model import CreateUserModel
from src.enums.user_role_enum import UserRole
from src.exception.user_exception import (ExceptionAdminCreateUserOutSCope, ExceptionCanNotCreateMaster, ExceptionMasterUpdateUserOutScope,
                                          ExceptionUserNotFound, ExceptionEmailExists)
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.enums.user_status_enum import UserStatusEnum

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.role_admin_create = {
            f"{UserRole.HANDLER.value}" : True,
            f"{UserRole.MANAGER.value}" : True,
            f"{UserRole.TASKER.value}" : True,
        }

    async def create_user(self, create_user_model: CreateUserModel, roles: list):
        # check users exist with email
        existing = await self.user_repository.get_user_by_email(create_user_model.email)
        if existing:
            raise ExceptionEmailExists()
        # master can create all exclude master
        # admin can create handler, manager, tasker

        if UserRole.ADMIN.value in roles:
            for role in create_user_model.roles:
                if f"{role}" not in self.role_admin_create:
                    raise ExceptionAdminCreateUserOutSCope()
        else:
            if UserRole.MASTER.value in create_user_model.roles:
                raise ExceptionCanNotCreateMaster()
        data_dump = create_user_model.model_dump()
        response = await self.user_repository.create_user(data_dump)
        return ResponseModel(data=response)

    async def get_user_by_id(self, user_id: str) -> ResponseModel:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ExceptionUserNotFound()
        return ResponseModel(data=user)

    async def update_user(self, user_id:str, update_user_model: UpdateUserModel, roles: list):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ExceptionUserNotFound()
        for role in user.get('roles'):
            if f"{role}" not in self.role_admin_create:
                raise ExceptionMasterUpdateUserOutScope()
        update_data = update_user_model.model_dump(exclude_unset=True)
        if update_data.get("roles"):
            for role in update_data.get("roles"):
                if f"{role}" not in self.role_admin_create:
                    raise ExceptionMasterUpdateUserOutScope()
        updated_user = await self.user_repository.update_user(user_id, update_data)
        return ResponseModel(data=updated_user)

    async def get_list_user(self, filters: FilterUserModel):
        list_user, total = await self.user_repository.get_list_users(filters.model_dump(exclude_unset=True))
        return ResponsePaginatedModel(data=list_user, total=total, offset=filters.offset)
    async def get_user_by_email(self, email:str):
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ExceptionUserNotFound()
        return ResponseModel(data=user)

