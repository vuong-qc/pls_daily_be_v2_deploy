from fastapi import APIRouter, Depends
from src.repositories.users.beanie_user_repository import BeanieUserRepository
from src.services.auth_service import AuthService
from src.models.auth.login_model import LoginModel

router = APIRouter(
    tags=["auth"],
)

def get_auth_service():
    user_repo = BeanieUserRepository()
    return AuthService(user_repo)

@router.post("/login")
async def login(
    login_data: LoginModel,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(login_data)
