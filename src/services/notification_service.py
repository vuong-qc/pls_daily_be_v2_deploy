from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.notification.notification_repository import NotificationRepository
from src.models.notification.request.filter_notification_model import FilterNotificationModel
from src.models.notification.request.update_notification_model import UpdateNotificationModel
from src.models.notification.request.create_notification_model import CreateNotificationModel
from src.models.notification.response.notification_response_model import NotificationResponse
from src.repositories.user.user_repository import UserRepository
from src.repositories.department.department_repository import DepartmentRepository
from src.models.department.request.filter_department_model import FilterDepartmentModel
from src.exception.department_exception import DepartmentException, DepartmentMessage, DepartmentStatusCode
from src.exception.notification_exception import NotificationException, NotificationStatusCode, NotificationMessage
from src.enums.notification_type_enum import NotificationTypeEnum

class NotificationService:
    def __init__(self, notification_repository: NotificationRepository, user_repository: UserRepository, department_repository: DepartmentRepository):
        self.notification_repository = notification_repository
        self.user_repository = user_repository
        self.department_repository = department_repository

    async def create_noti(self, user_id:str, create_notification_model: CreateNotificationModel):
        if create_notification_model.departments:
            filter_department = FilterDepartmentModel(limit=1, offset=0, list_ids=create_notification_model.departments)
            departments, total = await self.department_repository.get_list_departments(filter_department)
            if total != len(create_notification_model.departments):
                raise DepartmentException(DepartmentMessage.NOT_FOUND, DepartmentStatusCode.NOT_FOUND)

        create_notification_model.owner_id = user_id
        if create_notification_model.start_time and create_notification_model.end_time:
            if create_notification_model.start_time >= create_notification_model.end_time:
                raise NotificationException(NotificationMessage.START_TIME_GTE_END_TIME, NotificationStatusCode.START_TIME_GTE_END_TIME)

        noti = await self.notification_repository.create_noti(create_notification_model.model_dump())
        response = NotificationResponse.model_validate(noti)
        return ResponseModel(data=response)

    async def update_noti(self, noti_id:str,  user_id: str, update_notification_model: UpdateNotificationModel):
        if update_notification_model.departments:
            filter_department = FilterDepartmentModel(limit=1, offset=0, list_ids=update_notification_model.departments)
            departments, total = await self.department_repository.get_list_departments(filter_department)
            if total != len(update_notification_model.departments):
                raise DepartmentException(DepartmentMessage.NOT_FOUND, DepartmentStatusCode.NOT_FOUND)
        noti = await self.notification_repository.get_noti(noti_id)
        if not noti:
            raise NotificationException(NotificationMessage.NOT_FOUND, NotificationStatusCode.NOT_FOUND)
        if user_id != noti.owner_id:
            raise NotificationException(NotificationMessage.NOT_OWNER, NotificationStatusCode.NOT_OWNER)
        start_time = update_notification_model.start_time if update_notification_model.start_time else noti.start_time
        end_time = update_notification_model.end_time if update_notification_model.end_time else noti.end_time

        if start_time and end_time:
            if start_time > end_time:
                raise NotificationException(NotificationMessage.START_TIME_GTE_END_TIME, NotificationStatusCode.START_TIME_GTE_END_TIME)

        data = await self.notification_repository.update_noti(noti_id, update_notification_model.model_dump(exclude_unset=True))
        response = NotificationResponse.model_validate(data)
        return ResponseModel(data=response)
    async def delete_noti(self, user_id:str, noti_id:str):
        noti = await self.notification_repository.get_noti(noti_id)
        if not noti:
            raise NotificationException(NotificationMessage.NOT_FOUND, NotificationStatusCode.NOT_FOUND)
        if noti.owner_id != user_id:
            raise NotificationException(NotificationMessage.NOT_OWNER, NotificationStatusCode.NOT_OWNER)
        await self.notification_repository.delete_noti(noti_id)

    async def get_noti(self, noti_id:str):
        noti = await self.notification_repository.get_noti(noti_id)
        if not noti:
            raise NotificationException(NotificationMessage.NOT_FOUND, NotificationStatusCode.NOT_FOUND)

    async def get_list_noti(self, filter_department: FilterNotificationModel):
        list_noti, total = await self.notification_repository.get_list_noti(filter_department)
        list_response = []
        for noti in list_noti:
            response = NotificationResponse.model_validate(noti)
            list_response.append(response)
        return ResponsePaginatedModel(data=list_response, total=total, offset=filter_department.offset)

    async def get_my_noti(self, user_id:str):
        user = await self.user_repository.get_user_by_id(user_id)

        filters = FilterNotificationModel(limit=1, offset=0, viewer_ids=[user_id], type=NotificationTypeEnum.NOTIFICATION, departments=user.department)
        list_noti, total = await self.notification_repository.get_list_noti(filters)
        response = NotificationResponse.model_validate(list_noti[0]) if list_noti else None
        return ResponseModel(data=response)

    async def seen_noti(self, user_id:str, noti_id:str):
        noti = await self.notification_repository.add_viewer_noti(noti_id, user_id)
        if not noti:
            raise NotificationException(NotificationMessage.NOT_FOUND, NotificationStatusCode.NOT_FOUND)
        response = NotificationResponse.model_validate(noti)
        return ResponseModel(data=response)