from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.notification.beanie_notification_reposiotry import BeanieNotificationRepository
from src.models.notification.request.filter_notification_model import FilterNotificationModel
from src.models.notification.request.update_notification_model import UpdateNotificationModel
from src.models.notification.request.create_notification_model import CreateNotificationModel
from src.repositories.user.beanie_user_repository import BeanieUserRepository
from src.repositories.department.beanie_department_repository import BeanieDepartmentRepository
from fastapi import APIRouter, Query, Depends, status
from src.services.notification_service import NotificationService
from typing import Annotated
from src.utils.proxy_util import get_current_user_by_token

router = APIRouter(
    tags=["Notification"],
)
def get_notification_service() -> NotificationService:
    user_repository = BeanieUserRepository()
    department_repository = BeanieDepartmentRepository()
    notification_repository = BeanieNotificationRepository()
    return NotificationService(notification_repository, user_repository, department_repository)

@router.post("/create-notification",
             status_code=status.HTTP_201_CREATED,
             summary="Create new notification",
             response_model=ResponseModel,
             )
async def create_notification(
        notification: CreateNotificationModel,
        service: NotificationService = Depends(get_notification_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data["sub"]
    return await service.create_noti(user_id, notification)

@router.get("/get-list-notifications",
            status_code=status.HTTP_200_OK,
            summary="List all notifications",
            response_model=ResponsePaginatedModel,
            )
async def get_list_notifications(
        filters: Annotated[FilterNotificationModel, Query()],
        service: NotificationService = Depends(get_notification_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await service.get_list_noti(filters)

@router.put("/update-notification/{notification_id}",
            status_code=status.HTTP_202_ACCEPTED,
            summary="Update notification",
            response_model=ResponseModel,
)
async def update_notification(
        notification_id: str,
        notification_data: UpdateNotificationModel,
        service: NotificationService = Depends(get_notification_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data["sub"]
    return await service.update_noti(notification_id, user_id, notification_data)

@router.delete("/delete-notification/{notification_id}",
               status_code=status.HTTP_204_NO_CONTENT,
                summary="Delete notification", )
async def delete_notification(
        notification_id: str,
        service: NotificationService = Depends(get_notification_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data["sub"]
    return await service.delete_noti(user_id, notification_id)

@router.put("/seen-notification/{notification_id}",
            status_code=status.HTTP_202_ACCEPTED,
            summary="Seen a notification",
            response_model=ResponseModel,
            )
async def seen_notification(
        notification_id: str,
        service: NotificationService = Depends(get_notification_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data["sub"]
    return await service.seen_noti(user_id, notification_id)
@router.get("/get_my-notification",
            status_code=status.HTTP_200_OK,
            summary="Get my notification",
            response_model=ResponseModel,
            )
async def get_my_notification(
        service: NotificationService = Depends(get_notification_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id = user_data["sub"]
    return await service.get_my_noti(user_id)