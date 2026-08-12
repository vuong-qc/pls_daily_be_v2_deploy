from typing import Annotated

from src.models.plan.request.create_plan_model import CreatePlanModel
from src.models.plan.request.update_plan_model import UpdatePlanModel
from src.models.plan.request.filter_plan_model import FilterPlanModel
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.services.plan_service import PlanService
from src.repositories.plan.beanie_plan_repository import BeaniePlanRepository
from fastapi import APIRouter, Depends, Query, status
from src.utils.proxy_util import get_current_user_by_token

def get_plan_service():
    plan_repo = BeaniePlanRepository()
    return PlanService(plan_repo)

router = APIRouter(
    tags=["Plan"],
)

@router.post("/create-plan",
             status_code=status.HTTP_201_CREATED,
             summary="Create a new plan",
             response_model=ResponseModel)
async def create_plan(plan: CreatePlanModel,
                      service: PlanService = Depends(get_plan_service),
                      user_data: dict = Depends(get_current_user_by_token),
                      ):
    return await service.create_plan(plan)
@router.post("/update-plan/{plan_id}",
             status_code=status.HTTP_202_ACCEPTED,
             summary="Update a plan",
             response_model=ResponseModel)
async def update_plan(plan_id: str, plan_data: UpdatePlanModel,
                      service: PlanService = Depends(get_plan_service),
                      user_data: dict = Depends(get_current_user_by_token),
                      ):
    return await service.update_plan(plan_id, plan_data)
@router.delete("/delete-plan/{plan_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a plan", )
async def delete_plan(plan_id: str,
                      service: PlanService = Depends(get_plan_service),
                      user_data: dict = Depends(get_current_user_by_token),
                      ):
    return await service.delete_plan(plan_id)
@router.get("/get-list-plan",
            response_model=ResponsePaginatedModel,
            status_code=status.HTTP_200_OK,
            summary="List all plan in range date",)
async def get_list_plan(
        filters: Annotated[FilterPlanModel, Query()],
        service: PlanService = Depends(get_plan_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await service.get_list_plans(filters)