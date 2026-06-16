from abc import ABC, abstractmethod
from src.models.user.response.user_response_model import UserResponse
from src.models.user.response.project_user_model import ProjectUsername
class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_data: dict)-> UserResponse:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str)-> UserResponse | None:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str)-> UserResponse | None:
        pass
    @abstractmethod
    async def update_user(self, user_id:str, user_data: dict)-> UserResponse|None:
        pass

    @abstractmethod
    async def get_list_users(self, filters: dict)-> tuple[list[UserResponse], int]:
        pass
    @abstractmethod
    async def validate_password(self, password: str, user_id) -> bool:
        pass
    @abstractmethod
    async def get_all_user_not_match_id(self, list_id: list[str])-> list[ProjectUsername]:
        pass
    @abstractmethod
    async def get_all_user_match_id(self, list_id: list[str])-> list[ProjectUsername]:
        pass