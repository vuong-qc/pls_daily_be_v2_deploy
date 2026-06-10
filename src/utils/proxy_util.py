from src.services.auth_service import AuthService
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.utils.jwt_bearer_util import JWTBearerUtil
from fastapi import Depends
from src.repositories.user.beanie_user_repository import BeanieUserRepository
from src.exception.user_exception import ExceptionUserTokenExpired

def get_auth_service():
    repo = BeanieUserRepository()
    work_item_repo = BeanieWorkItemRepository()
    return AuthService(repo, work_item_repo)
async def get_current_user_by_token(
        payload: dict = Depends(JWTBearerUtil()),
        auth_service: AuthService = Depends(get_auth_service)
):
    user_id = payload["sub"]
    updated_at = payload["updated_at"]
    user = await auth_service.check_user_validity(user_id)
    user_updated_at = user.updated_at
    if user_updated_at > updated_at:
        raise ExceptionUserTokenExpired()
    return payload