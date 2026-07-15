from abc import ABC, abstractmethod

from src.models.department.request.filter_department_model import FilterDepartmentModel
from src.models.department.department_document import DepartmentDocument

class DepartmentRepository(ABC):
    @abstractmethod
    async def create_department(self, data: dict)-> DepartmentDocument:
        pass

    @abstractmethod
    async def update_department(self, department_id:str, data: dict)-> DepartmentDocument | None:
        pass

    @abstractmethod
    async def delete_department(self, department_id:str)-> None:
        pass

    @abstractmethod
    async def get_list_departments(self, filters: FilterDepartmentModel) -> tuple[list[DepartmentDocument], int]:
        pass

    @abstractmethod
    async def get_department_by_id(self, department_id:str)-> DepartmentDocument | None:
        pass