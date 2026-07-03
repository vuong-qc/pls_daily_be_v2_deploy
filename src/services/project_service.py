from src.enums.work_item_type import WorkItemType
from src.enums.sprint_status_enum import SprintStatusEnum
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.project.request.create_project_model import CreateProjectModel
from src.models.project.request.update_project_model import UpdateProjectModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.services.group_service import GroupService
from src.services.user_service import UserService
from src.models.project.response.project_response_base_model import ProjectInfo
from src.models.project.response.project_response_model import ProjectResponse
from src.exception.project_exception import ProjectMessage, ProjectStatusCode, ProjectException
from src.models.sprint.request.create_backlog_model import CreateBacklogModel
from src.default.backlog_name_default import DEFAULT_NAME

class ProjectService:
    def __init__(self, project_repository: WorkItemRepository, user_service: UserService, group_service: GroupService):
        self.project_repository = project_repository
        self.user_service = user_service
        self.group_service = group_service

    async def create_project(self, project_model: CreateProjectModel):
        if project_model.handler_id:
            for handler in project_model.handler_id:
                await self.user_service.get_user_by_id(handler)
        if project_model.parent:
            await self.group_service.get_group_by_id(project_model.parent)
        project = await self.project_repository.create_work_item(project_model.model_dump())
        #create backlog
        backlog = CreateBacklogModel(title=DEFAULT_NAME,parent=str(project.id))
        await self.project_repository.create_work_item(backlog.model_dump())
        return ResponseModel(data=ProjectResponse.model_validate(project))

    async def get_list_projects(self, filters: FilterWorkItemModel):
        projects, total = await self.project_repository.get_list_work_items(filters)
        list_projects = []
        for project in projects:
            response = ProjectResponse.model_validate(project)
            filter_children = FilterWorkItemModel(type=[WorkItemType.SPRINT],offset=0, limit=1, parent=str(project.id), status=[status for status in SprintStatusEnum if status!= SprintStatusEnum.CANCELED])
            total_children = await self.project_repository.count_work_item(filter_children)
            response.total_children = total_children

            filter_children.status = [SprintStatusEnum.PROCESSING]
            processing_children = await self.project_repository.count_work_item(filter_children)
            response.processing_children = processing_children

            list_projects.append(response)
        return ResponsePaginatedModel(data=list_projects, total=total, offset=filters.offset)

    async def update_project(self, project_id:str, project_model: UpdateProjectModel):
        project = await self.project_repository.update_work_item(project_id, project_model.model_dump(exclude_unset=True))
        if project:
            return ResponseModel(data=ProjectResponse.model_validate(project))
        raise ProjectException(ProjectMessage.NOT_FOUND, ProjectStatusCode.NOT_FOUND)
    async def delete_project(self, project_id:str):
        project = await self.project_repository.delete_work_item(project_id)
        return ResponseModel()

    async def get_project_by_id(self, project_id:str):
        project = await self.project_repository.get_work_item_by_id(project_id)
        if project:
            return ResponseModel(data=ProjectInfo.model_validate(project))
        raise ProjectException(ProjectMessage.NOT_FOUND, ProjectStatusCode.NOT_FOUND)