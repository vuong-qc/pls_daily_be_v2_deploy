from fastapi import APIRouter, Depends

from src.models.response_model import ResponseModel
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.repositories.user.beanie_user_repository import BeanieUserRepository
from src.services.auth_service import AuthService
from src.models.auth.login_model import LoginModel

router = APIRouter(
    tags=["auth"],
)

def get_auth_service():
    user_repo = BeanieUserRepository()
    work_item_repo = BeanieWorkItemRepository()
    return AuthService(user_repo, work_item_repo)

@router.post("/login",
             response_model=ResponseModel)
async def login(
    login_data: LoginModel,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(login_data)
