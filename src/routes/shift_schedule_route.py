from src.services.shift_schedule_service import ShiftScheduleService
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.shift_schedule.request.create_shift_schedule_model import CreateShiftScheduleModel
from src.models.shift_schedule.request.update_shift_schedule_model import UpdateShiftScheduleModel
from src.models.shift_schedule.request.filter_shift_schedule_model import FilterShiftScheduleModel
from fastapi import APIRouter, Query, Depends, status
from typing import Annotated
from src.utils.proxy_util import get_current_user_by_token
from src.repositories.shift_schedule.beanie_shift_schedule_repository import BeanieShiftScheduleRepository

def get_shift_schedule_service():
    shift_schedule_repository = BeanieShiftScheduleRepository()
    return ShiftScheduleService(shift_schedule_repository)
router = APIRouter(
    tags=["Shift Schedule"],
)

@router.post("/create-shift-schedule",
             response_model=ResponseModel,
             status_code=status.HTTP_201_CREATED,
             summary="Create Shift Schedule",
             )
async def create_shift_schedule(
        data: CreateShiftScheduleModel,
        service: ShiftScheduleService = Depends(get_shift_schedule_service),
        user_token: dict = Depends(get_current_user_by_token),
):
    return await service.create_shift_schedule(data)
@router.put("/update-shift-schedule/{shift_schedule_id}",
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            summary="Update Shift Schedule",
            )
async def update_shift_schedule(
        shift_schedule_id: str,
        data: UpdateShiftScheduleModel,
        service: ShiftScheduleService = Depends(get_shift_schedule_service),
        user_token: dict = Depends(get_current_user_by_token),
):
    return await service.update_shift_schedule(shift_schedule_id, data)

@router.get("/get-list-shift-schedule",
            response_model=ResponsePaginatedModel,
            status_code=status.HTTP_200_OK,
            summary="Get Shift Schedule",
            )
async def get_shift_schedule_list(
        filters: Annotated[FilterShiftScheduleModel, Query()],
        service: ShiftScheduleService = Depends(get_shift_schedule_service),
        user_token: dict = Depends(get_current_user_by_token),
):
    return await service.get_list_shift_schedules(filters)

@router.delete("/delete-shift-schedule/{shift_schedule_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete Shift Schedule",
               )
async def delete_shift_schedule(
        shift_schedule_id: str,
        service: ShiftScheduleService = Depends(get_shift_schedule_service),
        user_token: dict = Depends(get_current_user_by_token),
):
    return await service.delete_shift_schedule(shift_schedule_id)