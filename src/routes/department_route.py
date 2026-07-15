from src.repositories.department.beanie_department_repository import BeanieDepartmentRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.department.request.filter_department_model import FilterDepartmentModel
from src.models.department.request.create_department_model import CreateDepartmentModel
from src.models.department.request.update_department_model import UpdateDepartmentModel
from fastapi import APIRouter, status, Depends, Query
from typing import Annotated
from src.enums.user_role_enum import UserRole
from src.utils.role_checker_util import RoleCheckerUtil
from src.utils.proxy_util import get_current_user_by_token
from src.services.department_service import DepartmentService
from src.routes.chatbot_token_route import ChatbotTokenService, get_chatbot_service

router = APIRouter(
    tags=["department"],
)

def get_department_service(
        chatbot_service: ChatbotTokenService = Depends(get_chatbot_service),
) -> DepartmentService:
    department_repo = BeanieDepartmentRepository()
    return DepartmentService(department_repo, chatbot_service)

@router.post("/create-department",
             response_model=ResponseModel,
             status_code=status.HTTP_201_CREATED,
             description="Create a new department by master",
             dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value]))]
             )
async def create_department(department: CreateDepartmentModel,
                            service: DepartmentService = Depends(get_department_service),
                            user_data: dict = Depends(get_current_user_by_token),
                            ):
    return await service.create_department(department)

@router.put("/update-department/{department_id}",
            status_code=status.HTTP_202_ACCEPTED,
            response_model=ResponseModel,
            dependencies=[Depends(RoleCheckerUtil([UserRole.MASTER.value]))],
            summary="Update a department",
            description="Update a department by master"
            )
async def update_department(department_id: str, department: UpdateDepartmentModel,
                            service: DepartmentService = Depends(get_department_service),
                            user_data: dict = Depends(get_current_user_by_token),
                            ):
    return await service.update_department(department_id, department)

@router.delete("/delete-department/{department_id}",
                status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a department",
               description="Delete a department by master"
               )
async def delete_department(department_id: str,
                            service: DepartmentService = Depends(get_department_service),
                            user_data: dict = Depends(get_current_user_by_token),
                            ):
    return await service.delete_department(department_id)
@router.get("/list-departments",
            description="List all departments",
            summary="List all departments",
            response_model=ResponsePaginatedModel,
            status_code=status.HTTP_200_OK, )
async def list_departments(
        query: Annotated[FilterDepartmentModel, Query()],
        service: DepartmentService = Depends(get_department_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await service.get_list_departments(query)