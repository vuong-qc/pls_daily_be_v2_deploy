from abc import ABC, abstractmethod
from src.models.notification.notification_document import NotificationDocument
from src.models.notification.request.filter_notification_model import FilterNotificationModel

class NotificationRepository(ABC):
    @abstractmethod
    async def create_noti(self, data: dict)->NotificationDocument:
        pass
    @abstractmethod
    async def update_noti(self, noti_id:str, data: dict)->NotificationDocument | None:
        pass
    @abstractmethod
    async def delete_noti(self, noti_id: str):
        pass
    @abstractmethod
    async def get_noti(self, noti_id: str)->NotificationDocument | None:
        pass
    @abstractmethod
    async def get_list_noti(self, filters: FilterNotificationModel) -> tuple[list[NotificationDocument], int]:
        pass
    @abstractmethod
    async def add_viewer_noti(self, noti_id:str, user_id: str):
        pass