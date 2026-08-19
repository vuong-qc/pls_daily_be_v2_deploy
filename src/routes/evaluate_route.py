from src.models.evaluate.request.filter_evaluate_model import FilterEvaluateModel
from src.models.evaluate.request.create_evaluate_model import CreateEvaluateModel
from src.models.evaluate.request.update_evaluate_model import UpdateEvaluateModel
from src.repositories.evaluate.evaluate_repository import EvaluateRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.evaluate.beanie_evaluate_repository import BeanieEvaluateRepository
from fastapi import APIRouter, Depends, Query, status
from src.services.evaluate_service import EvaluateService
from src.utils.proxy_util import get_current_user_by_token
from typing import Annotated

router = APIRouter(
    tags=["evaluate"],
)

def get_evaluate_service():
    evaluate_repo = BeanieEvaluateRepository()
    return EvaluateService(evaluate_repo)

@router.post("/create-evaluate",
             response_model=ResponseModel,
             status_code=status.HTTP_201_CREATED,
             summary="Create an Evaluate")
async def create_evaluate_service(
        evaluate_model: CreateEvaluateModel,
        service: EvaluateService = Depends(get_evaluate_service),
        user_data: dict = Depends(get_current_user_by_token)
        ):
    return await service.create_evaluate(evaluate_model)

@router.put("/update-evaluate/{evaluate_id}",
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            summary="Update an Evaluate")
async def update_evaluate_service(
        evaluate_id:str,
        evaluate_model: UpdateEvaluateModel,
        service: EvaluateService = Depends(get_evaluate_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data.get("sub")
    roles = user_data.get("roles")
    return await service.update_evaluate(evaluate_id, evaluate_model, roles, user_id)

@router.delete("/delete-evaluate/{evaluate_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete an Evaluate"
               )
async def delete_evaluate_service(
        evaluate_id:str,
        service: EvaluateService = Depends(get_evaluate_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data.get("sub")
    roles = user_data.get("roles")
    return await service.delete_evaluate(evaluate_id, user_id, roles)
@router.get("/list-evaluates",
            status_code=status.HTTP_200_OK,
            summary="List all Evaluates",
            response_model=ResponsePaginatedModel,)
async def list_evaluates(
        query: Annotated[FilterEvaluateModel, Query()],
        service: EvaluateService = Depends(get_evaluate_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await service.get_list_evaluate(query)