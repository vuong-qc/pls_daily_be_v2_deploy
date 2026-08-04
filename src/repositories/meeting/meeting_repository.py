from abc import ABC, abstractmethod
from src.models.meeting.request.filter_meeting_model import FilterMeetingModel
from src.models.meeting.meeting_document import MeetingDocument

class MeetingRepository(ABC):
    @abstractmethod
    async def create_meeting(self, data: dict)-> MeetingDocument:
        pass

    @abstractmethod
    async def update_meeting(self, meeting_id: str, data: dict)-> MeetingDocument|None:
        pass

    @abstractmethod
    async def delete_meeting(self, meeting_id: str):
        pass

    @abstractmethod
    async def get_list_of_meetings(self, filters: FilterMeetingModel) -> tuple[list[MeetingDocument],int]:
        pass

    @abstractmethod
    async def get_meeting_by_id(self, meeting_id: str)->MeetingDocument|None:
        pass

    @abstractmethod
    async def add_participant(self, meeting_id: str, user_id:str)->MeetingDocument:
        pass
    async def remove_participant(self, meeting_id: str, user_id:str)->MeetingDocument:
        pass