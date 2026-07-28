from typing import Optional

from src.repositories.shift_schedule.shift_schedule_repository import ShiftScheduleRepository
from src.models.shift_schedule.request.create_shift_schedule_model import CreateShiftScheduleModel
from src.models.shift_schedule.request.update_shift_schedule_model import UpdateShiftScheduleModel
from src.models.shift_schedule.request.filter_shift_schedule_model import FilterShiftScheduleModel
from src.models.shift_schedule.response.shift_schedule_response_model import ShiftScheduleResponseModel
from src.exception.shift_schedule_exception import ShiftScheduleException, ShiftScheduleStatusCode, ShiftScheduleMessage
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.enums.weekday_enum import WeekdayEnum

class ShiftScheduleService:
    def __init__(self, repository: ShiftScheduleRepository):
        self.repository = repository

    async def create_shift_schedule(self, shift_schedule: CreateShiftScheduleModel):
        if shift_schedule.end_time<=shift_schedule.start_time:
            raise ShiftScheduleException(ShiftScheduleMessage.END_LTE_START, ShiftScheduleStatusCode.END_LTE_START)

        # check case
        await self._check_conflict_schedule(shift_schedule.start_time, shift_schedule.end_time, shift_schedule.weekday, shift_schedule.user_id)
        doc = await self.repository.create_shift_schedule(shift_schedule.model_dump())
        response = ShiftScheduleResponseModel.model_validate(doc)
        return ResponseModel(data=response)

    async def update_shift_schedule(self, schedule_id:str, shift_schedule: UpdateShiftScheduleModel):
        old_schedule = await self.repository.get_shift_schedule_by_id(schedule_id)
        if not old_schedule:
            raise ShiftScheduleException(ShiftScheduleMessage.NOT_FOUND, ShiftScheduleStatusCode.NOT_FOUND)
        start = shift_schedule.start_time if shift_schedule.start_time else old_schedule.start_time
        end = shift_schedule.end_time  if shift_schedule.end_time else old_schedule.end_time

        if end<=start:
            raise ShiftScheduleException(ShiftScheduleMessage.END_LTE_START, ShiftScheduleStatusCode.END_LTE_START)

        await self._check_conflict_schedule(start, end, old_schedule.weekday, old_schedule.user_id, schedule_id)
        update_schedule = await self.repository.update_shift_schedule(schedule_id, shift_schedule.model_dump(exclude_unset=True))
        response = ShiftScheduleResponseModel.model_validate(update_schedule)
        return ResponseModel(data=response)

    async def get_shift_schedule(self, shift_schedule_id:str):
        shift_schedule = await self.repository.get_shift_schedule_by_id(shift_schedule_id)
        if not shift_schedule:
            raise ShiftScheduleException(ShiftScheduleMessage.NOT_FOUND, ShiftScheduleStatusCode.NOT_FOUND)

        response = ShiftScheduleResponseModel.model_validate(shift_schedule)
        return ResponseModel(data=response)

    async def delete_shift_schedule(self, shift_schedule_id:str):
        return await self.repository.delete_shift_schedule(shift_schedule_id)

    async def get_list_shift_schedules(self, filters: FilterShiftScheduleModel):
        schedules, total = await self.repository.get_list_of_shift_schedules(filters)
        list_shift_schedules = []
        for schedule in schedules:
            response = ShiftScheduleResponseModel.model_validate(schedule)
            list_shift_schedules.append(response)
        return ResponsePaginatedModel(data=list_shift_schedules, total=total, offset=filters.offset if filters.offset else 0)

    async def _check_conflict_schedule(self, start_time:int, end_time:int, weekday:WeekdayEnum, user_id:str, schedule_id:Optional[str] = None):
        filters = FilterShiftScheduleModel(user_id=user_id, weekday=weekday)
        schedules, total = await self.repository.get_list_of_shift_schedules(filters)
        if schedules:
            for schedule in schedules:
                if schedule_id and str(schedule.id )== schedule_id:
                    continue
                if start_time <= schedule.start_time and schedule.end_time <= end_time:
                    raise ShiftScheduleException(ShiftScheduleMessage.CONFLICT, ShiftScheduleStatusCode.CONFLICT)
                if end_time >= schedule.start_time >= start_time:
                    raise ShiftScheduleException(ShiftScheduleMessage.CONFLICT, ShiftScheduleStatusCode.CONFLICT)
                if end_time >= schedule.end_time >= start_time:
                    raise ShiftScheduleException(ShiftScheduleMessage.CONFLICT, ShiftScheduleStatusCode.CONFLICT)