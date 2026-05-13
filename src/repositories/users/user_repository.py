from abc import ABC, abstractmethod
class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_data: dict)-> dict:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str)-> dict | None:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str)-> dict | None:
        pass
    @abstractmethod
    async def update_user(self, user_id:str, user_data: dict)-> dict|None:
        pass

    @abstractmethod
    async def get_list_users(self, filters: dict)-> tuple[list[dict], int]:
        pass