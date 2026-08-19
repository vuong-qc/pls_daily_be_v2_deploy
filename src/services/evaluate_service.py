from src.models.evaluate.request.filter_evaluate_model import FilterEvaluateModel
from src.models.evaluate.request.create_evaluate_model import CreateEvaluateModel
from src.models.evaluate.request.update_evaluate_model import UpdateEvaluateModel
from src.repositories.evaluate.evaluate_repository import EvaluateRepository
from src.models.evaluate.response.evaluate_response_model import EvaluateResponseModel
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.exception.evaluate_exception import EvaluateException, EvaluateMessage, EvaluateStatusCode
from src.enums.user_role_enum import UserRole

class EvaluateService:
    def __init__(self, repository: EvaluateRepository):
        self.repository = repository

    async def create_evaluate(self, data: CreateEvaluateModel):
        evaluate = await self.repository.create_evaluate(data.model_dump())
        response = EvaluateResponseModel.model_validate(evaluate)
        return ResponseModel(data=response)

    async def update_evaluate(self, evl_id:str, data: UpdateEvaluateModel, roles: list[int], user_id: str):
        if UserRole.MANAGER not in roles:
            evaluate = await self.repository.get_evaluate_by_id(evl_id)
            if not evaluate:
                raise EvaluateException(EvaluateMessage.NOT_FOUND, EvaluateStatusCode.NOT_FOUND)
            if evaluate.creator_id != user_id:
                raise EvaluateException(EvaluateMessage.CREATOR_NOT_MATCH, EvaluateStatusCode.CREATOR_NOT_MATCH)
        upt_res = await self.repository.update_evaluate(evl_id, data.model_dump(exclude_unset=True))

        if not upt_res:
            raise EvaluateException(EvaluateMessage.NOT_FOUND, EvaluateStatusCode.NOT_FOUND)

        response = EvaluateResponseModel.model_validate(upt_res)
        return ResponseModel(data=response)

    async def get_evaluate_by_id(self, evaluate_id: str):
        evaluate = await self.repository.get_evaluate_by_id(evaluate_id)
        response = EvaluateResponseModel.model_validate(evaluate)
        return ResponseModel(data=response)

    async def get_list_evaluate(self, filters: FilterEvaluateModel):
        list_evaluate, total = await self.repository.get_list_evaluate(filters)
        list_response = []
        for evaluate in list_evaluate:
            response = EvaluateResponseModel.model_validate(evaluate)
            list_response.append(response)
        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

    async def delete_evaluate(self, evaluate_id: str, user_id: str, roles: list[int]):
        if UserRole.MANAGER not in roles:
            evaluate = await self.repository.get_evaluate_by_id(evaluate_id)
            if not evaluate:
                raise EvaluateException(EvaluateMessage.NOT_FOUND, EvaluateStatusCode.NOT_FOUND)
            if evaluate.creator_id != user_id:
                raise EvaluateException(EvaluateMessage.CREATOR_NOT_MATCH, EvaluateStatusCode.CREATOR_NOT_MATCH)

        await self.repository.delete_evaluate(evaluate_id)