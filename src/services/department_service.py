from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.department.request.filter_department_model import FilterDepartmentModel
from src.models.department.response.department_response_model import DepartmentResponseModel
from src.models.department.request.create_department_model import CreateDepartmentModel
from src.models.department.request.update_department_model import UpdateDepartmentModel
from src.repositories.department.department_repository import DepartmentRepository
from src.exception.department_exception import DepartmentException, DepartmentStatusCode, DepartmentMessage
from src.services.chatbot_token_service import ChatbotTokenService

class DepartmentService:
    def __init__(self, department_repository: DepartmentRepository, chatbot_service: ChatbotTokenService):
        self.department_repository = department_repository
        self.chatbot_service = chatbot_service
    async def create_department(self, department_data: CreateDepartmentModel) -> ResponseModel:
        if department_data.chatbot_token_id:
            await self.chatbot_service.get_chatbot_token(department_data.chatbot_token_id)
        department = await self.department_repository.create_department(department_data.model_dump(exclude_unset=True))
        response = DepartmentResponseModel.model_validate(department)
        return ResponseModel(data=response)

    async def update_department(self, department_id: str, department_data: UpdateDepartmentModel) -> ResponseModel:
        if department_data.chatbot_token_id:
            await self.chatbot_service.get_chatbot_token(department_data.chatbot_token_id)

        department = await self.update_department(department_id, department_data.model_dump(exclude_unset=True))
        if not department:
            raise DepartmentException(DepartmentMessage.NOT_FOUND, DepartmentStatusCode.NOT_FOUND)
        response = DepartmentResponseModel.model_validate(department)
        return ResponseModel(data=response)

    async def delete_department(self, department_id: str) -> None:
        await self.delete_department(department_id)

    async def get_department_by_id(self, department_id: str) -> ResponseModel:
        department = await self.department_repository.get_department_by_id(department_id)
        if not department:
            raise DepartmentException(DepartmentMessage.NOT_FOUND, DepartmentStatusCode.NOT_FOUND)
        response = DepartmentResponseModel.model_validate(department)
        return ResponseModel(data=response)

    async def get_list_departments(self, filters: FilterDepartmentModel) -> ResponsePaginatedModel:
        departments, total = await self.department_repository.get_list_departments(filters)
        list_response = []
        for department in departments:
            list_response.append(DepartmentResponseModel.model_validate(department))

        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)