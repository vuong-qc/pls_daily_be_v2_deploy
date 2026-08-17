from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.repositories.log.beanie_log_repository import BeanieLogRepository
from src.services.log_service import LogService
from src.utils.proxy_util import get_current_user_by_token
from src.models.log.request.create_log_model import CreateLogModel
from src.models.log.request.filter_log_model import FilterLogModel
from src.repositories.user.beanie_user_repository import BeanieUserRepository


router = APIRouter(
    tags=["log"],
)
def get_log_service():
    log_repo = BeanieLogRepository()
    user_repository = BeanieUserRepository()
    return LogService(log_repo, user_repository)

@router.post("/create-log")
async def create_log(
        create_log_model: CreateLogModel,
        user_data: dict = Depends(get_current_user_by_token),
        log_service: LogService = Depends(get_log_service)
):
    user_id = user_data["sub"]
    create_log_model.user = user_id
    return await log_service.create_log(create_log_model)

@router.get("/get-list-logs")
async def get_list_logs(
        filter_log_model: Annotated[FilterLogModel, Query()],
        user_data: dict = Depends(get_current_user_by_token),
        log_service: LogService = Depends(get_log_service)
):
    return await log_service.get_logs(filter_log_model)