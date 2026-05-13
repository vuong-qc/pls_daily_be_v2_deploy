from src.repositories.users.user_repository import UserRepository
from src.exception.user_exception import ExceptionUserIsNotValid
from src.utils.security_password_util import SecurityPasswordUtil
from fastapi import HTTPException
from src.enums.user_status_enum import UserStatusEnum
from src.utils.jwt_bearer_util import JWTBearerUtil
from src.models.response_model import ResponseModel, ResponseLoginModel
from src.configs import settings
from src.models.user.create_user_model import CreateUserModel
from src.enums.user_role_enum import UserRole
from src.models.auth.login_model import LoginModel

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

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
                updated_at = new_user.get("updated_at")
                token = JWTBearerUtil.generate_access_token(new_user.get("id"), new_user.get("roles", []), updated_at)
                return ResponseModel(data=ResponseLoginModel(access_token=token).model_dump())

            raise HTTPException(status_code=401, detail="Email Invalids")
        if user.get("status") != UserStatusEnum.ACTIVE:
            raise ExceptionUserIsNotValid
        is_valid = SecurityPasswordUtil.verify_password(
            password,
            user.get("password","")
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Incorrect Password")

        updated_at = user.get("updated_at")
        token = JWTBearerUtil.generate_access_token(user.get("id"), user.get("roles",[]), updated_at)
        return ResponseModel(data=ResponseLoginModel(access_token= token).model_dump())
    async def check_user_validity(self, user_id: str):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user["status"] != UserStatusEnum.ACTIVE.value:
            raise ExceptionUserIsNotValid()
        return user