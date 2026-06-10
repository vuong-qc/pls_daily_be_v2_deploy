from abc import ABC, abstractmethod

from src.models.session.request.filter_session_model import FilterSessionModel
from src.models.session.session_document import SessionDocument

class SessionRepository(ABC):
    @abstractmethod
    async def get_session_by_id(self, session_id: str)->SessionDocument|None:
        pass

    @abstractmethod
    async def get_list_session(self, filters: FilterSessionModel)-> tuple[list[SessionDocument], int]:
        pass

    @abstractmethod
    async def create_session(self, session: dict)-> SessionDocument:
        pass

    @abstractmethod
    async def update_session(self, session_id:str, session_data: dict)-> SessionDocument | None:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str)-> None:
        pass