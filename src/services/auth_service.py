from src.repositories.user.user_repository import UserRepository
from src.exception.user_exception import ExceptionUserIsNotValid
from fastapi import HTTPException
from src.enums.user_status_enum import UserStatusEnum
from src.utils.jwt_bearer_util import JWTBearerUtil
from src.models.response_model import ResponseModel, ResponseLoginModel
from src.configs import settings
from src.models.user.request.create_user_model import CreateUserModel
from src.enums.user_role_enum import UserRole
from src.models.auth.login_model import LoginModel
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.sprint.request.create_backlog_model import CreateBacklogModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.enums.work_item_type import WorkItemType
from src.default.backlog_name_default import DEFAULT_NAME

class AuthService:
    def __init__(self, user_repository: UserRepository, work_item_repository: WorkItemRepository):
        self.user_repository = user_repository
        self.work_item_repository = work_item_repository

    async def login(self, login_data: LoginModel) -> ResponseModel:
        email =  login_data.email
        password = login_data.password
        user = await self.user_repository.get_user_by_email(email)

        if not user:
            if email == settings.ADMIN_MAIL:
                user_model = CreateUserModel(
                    password= password,
                    email= email,
                    name="master",
                    phone="",
                    roles=[UserRole.MASTER.value],
                    gender=1,
                    traineeStatus=0
                )
                new_user = await self.user_repository.create_user(user_model.model_dump())
                updated_at = new_user.updated_at
                token = JWTBearerUtil.generate_access_token(str(new_user.id), new_user.roles, updated_at)
                return ResponseModel(data=ResponseLoginModel(access_token=token))

            raise HTTPException(status_code=401, detail="Email Invalids")
        if user.status != UserStatusEnum.ACTIVE:
            raise ExceptionUserIsNotValid
        is_valid = await self.user_repository.validate_password(password, user.id)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Incorrect Password")

        updated_at = user.updated_at
        token = JWTBearerUtil.generate_access_token(str(user.id), user.roles, updated_at)

        # check user has backlog => create backlog
        filters = FilterWorkItemModel(type=[WorkItemType.BACKLOG], parent=str(user.id),limit=1,offset=0)
        user_backlog, total = await self.work_item_repository.get_list_work_items(filters)
        if total < 1:
            backlog_model = CreateBacklogModel(parent=str(user.id),title=DEFAULT_NAME)
            await self.work_item_repository.create_work_item(backlog_model.model_dump())


        return ResponseModel(data=ResponseLoginModel(access_token= token))
    async def check_user_validity(self, user_id: str):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.status != UserStatusEnum.ACTIVE.value:
            raise ExceptionUserIsNotValid()
        return user