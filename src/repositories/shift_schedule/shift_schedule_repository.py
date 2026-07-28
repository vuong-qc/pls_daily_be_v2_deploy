from abc import ABC, abstractmethod
from src.models.shift_schedule.request.filter_shift_schedule_model import FilterShiftScheduleModel
from src.models.shift_schedule.shift_schedule_document import ShiftScheduleDocument

class ShiftScheduleRepository(ABC):
    @abstractmethod
    async def create_shift_schedule(self, data: dict)-> ShiftScheduleDocument:
        pass

    @abstractmethod
    async def update_shift_schedule(self, shift_schedule_id: str, data: dict)-> ShiftScheduleDocument|None:
        pass

    @abstractmethod
    async def delete_shift_schedule(self, shift_schedule_id: str):
        pass

    @abstractmethod
    async def get_list_of_shift_schedules(self, filters: FilterShiftScheduleModel) -> tuple[list[ShiftScheduleDocument],int]:
        pass

    @abstractmethod
    async def get_shift_schedule_by_id(self, shift_schedule_id: str)->ShiftScheduleDocument|None:
        pass
