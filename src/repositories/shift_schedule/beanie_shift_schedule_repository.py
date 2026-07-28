from beanie import PydanticObjectId
from beanie.operators import Set, GTE, LTE

from src.repositories.shift_schedule.shift_schedule_repository import ShiftScheduleRepository
from src.models.shift_schedule.request.filter_shift_schedule_model import FilterShiftScheduleModel
from src.models.shift_schedule.shift_schedule_document import ShiftScheduleDocument

class BeanieShiftScheduleRepository(ShiftScheduleRepository):
    async def create_shift_schedule(self, data: dict)-> ShiftScheduleDocument:
        shift_schedule = ShiftScheduleDocument(**data)
        return await shift_schedule.insert()

    async def update_shift_schedule(self, shift_schedule_id: str, data: dict)-> ShiftScheduleDocument|None:
        schedule = await ShiftScheduleDocument.get(shift_schedule_id)
        if schedule:
            return await schedule.update(Set(data))
        return None

    async def delete_shift_schedule(self, shift_schedule_id: str):
        shift_schedule = await ShiftScheduleDocument.get(shift_schedule_id)
        if shift_schedule:
            return await shift_schedule.delete()

    async def get_list_of_shift_schedules(self, filters: FilterShiftScheduleModel) -> tuple[list[ShiftScheduleDocument],int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = int(filter_dump.pop('offset', 0))
        limit = int(filter_dump.pop('limit', 10))

        if filters.start_time:
            filter_dump.update(
                GTE(ShiftScheduleDocument.start_time, filter_dump.pop('start_time')),
            )
        if filters.end_time:
            filter_dump.update(
                LTE(ShiftScheduleDocument.end_time, filter_dump.pop('end_time')),
            )
        query = ShiftScheduleDocument.find(filter_dump)
        count = await query.count()
        list_shift_schedules = await query.skip(offset).limit(limit).to_list()
        return list_shift_schedules, count

    async def get_shift_schedule_by_id(self, shift_schedule_id: str)->ShiftScheduleDocument|None:
        return await ShiftScheduleDocument.get(shift_schedule_id)
