from src.repositories.plan.plan_repository import PlanRepository
from src.models.plan.request.create_plan_model import CreatePlanModel
from src.models.plan.request.update_plan_model import UpdatePlanModel
from src.models.plan.request.filter_plan_model import FilterPlanModel
from src.models.plan.response.plan_response_model import PlanResponseModel
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.exception.plan_exception import PlanException, PlanMessage, PlanStatusCode

class PlanService:
    def __init__(self, plan_repository: PlanRepository):
        self.plan_repository = plan_repository

    async def create_plan(self, data: CreatePlanModel):
        plan = await self.plan_repository.create_plan(data.model_dump())
        response = PlanResponseModel.model_validate(plan)
        return ResponseModel(data=response)
    async def update_plan(self, plan_id: str, data: UpdatePlanModel):
        plan = await self.plan_repository.update_plan(plan_id, data.model_dump(exclude_unset=True))
        if not plan:
            raise PlanException(PlanMessage.NOT_FOUND, PlanStatusCode.NOT_FOUND)
        response = PlanResponseModel.model_validate(plan)
        return ResponseModel(data=response)

    async def delete_plan(self, plan_id: str):
        plan = await self.plan_repository.delete_plan(plan_id)
        return
    async def get_plan(self, plan_id: str):
        plan = await self.plan_repository.get_plan_by_id(plan_id)
        if not plan:
            raise PlanException(PlanMessage.NOT_FOUND, PlanStatusCode.NOT_FOUND)
        response = PlanResponseModel.model_validate(plan)
        return ResponseModel(data=response)

    async def get_list_plans(self, filters: FilterPlanModel):
        plans, total = await self.plan_repository.get_list_plan(filters)
        list_plans = []
        for plan in plans:
            response = PlanResponseModel.model_validate(plan)
            list_plans.append(response)
        return ResponsePaginatedModel(data=list_plans, total=total, offset=filters.offset)