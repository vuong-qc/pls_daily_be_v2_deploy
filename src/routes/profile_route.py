from src.services.user_service import UserService
from src.routes.user_route import get_user_service
from src.utils.proxy_util import get_current_user_by_token
from fastapi import APIRouter, Depends
from src.models.user.request.update_user_model import UpdateProfileModel

router = APIRouter(
    tags=["profile"]
)


@router.get("/get-profile")
async def get_user_profile(
        user_service: UserService = Depends(get_user_service),
        current_user: dict = Depends(get_current_user_by_token)
):
    user_id = current_user["sub"]
    return await user_service.get_user_by_id(user_id,)


@router.put("/update-profile")
async def update_profile(
        profile_update: UpdateProfileModel,
        user_service: UserService = Depends(get_user_service),
        current_user: dict = Depends(get_current_user_by_token)
):
    user_id = current_user["sub"]
    return await user_service.update_user(user_id, profile_update)
