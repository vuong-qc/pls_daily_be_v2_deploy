from beanie import PydanticObjectId

from src.models.department.department_document import DepartmentDocument
from src.repositories.department.department_repository import DepartmentRepository
from beanie.operators import Set, In
from src.models.department.request.filter_department_model import FilterDepartmentModel

class BeanieDepartmentRepository(DepartmentRepository):
    async def get_department_by_id(self, department_id:str) -> DepartmentDocument | None:
        return await DepartmentDocument.get(department_id)
    async def get_list_departments(self, filters: FilterDepartmentModel) -> tuple[list[DepartmentDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        limit = filter_dump.pop('limit', 10)
        offset = filter_dump.pop('offset', 0)
        if filters.list_ids:
            filter_dump.update(
                In(DepartmentDocument.id, [PydanticObjectId(id) for id in filter_dump.pop('list_ids')]),
            )
        query = DepartmentDocument.find(filter_dump)
        count = await query.count()
        list_departments = await query.skip(offset).limit(limit).to_list()
        return list_departments, count

    async def delete_department(self, department_id:str) -> None:
        department = await DepartmentDocument.get(department_id)
        if department:
            await department.delete()

    async def update_department(self, department_id:str, data: dict) -> DepartmentDocument | None:
        department = await DepartmentDocument.get(department_id)
        if department:
            await department.update(Set(data))
            return department
        return None

    async def create_department(self, data: dict) -> DepartmentDocument:
        department = DepartmentDocument(**data)
        return await department.insert()