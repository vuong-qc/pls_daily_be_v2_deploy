from src.models.group.request.create_group_model import CreateGroupModel
from src.models.group.request.update_group_model import UpdateGroupModel
from src.models.group.request.filter_group_model import FilterGroupModel
from src.repositories.group.group_repository import GroupRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.exception.group_exception import GroupException, GroupMessage, GroupStatusCode

class GroupService:
    def __init__(self, group_repository: GroupRepository):
        self.group_repository = group_repository
    async def create_group(self, request: CreateGroupModel):
        data = await self.group_repository.create_group(request.model_dump())
        return ResponseModel(data=data)

    async def update_group(self, group_id:str, request: UpdateGroupModel, user_id: str):
        # check is owner of group
        group = await self.group_repository.get_group_by_id(group_id)
        if not group:
            raise GroupException(message=GroupMessage.NOT_FOUND,code=GroupStatusCode.NOT_FOUND)
        if group.created_by != user_id:
            raise GroupException(message=GroupMessage.NOT_CREATOR,code=GroupStatusCode.NOT_CREATOR)

        updated_group = await self.group_repository.update_group(group_id, request.model_dump(exclude_unset=True))
        if updated_group:
            return ResponseModel(data=updated_group)
        raise GroupException(message=GroupMessage.NOT_FOUND,code=GroupStatusCode.NOT_FOUND)

    async def delete_group(self, group_id:str, user_id: str):
        group = await self.group_repository.get_group_by_id(group_id)
        if not group:
            raise GroupException(message=GroupMessage.NOT_FOUND,code=GroupStatusCode.NOT_FOUND)
        if group.created_by != user_id:
            raise GroupException(message=GroupMessage.NOT_CREATOR,code=GroupStatusCode.NOT_CREATOR)
        await self.group_repository.delete_group(group_id)
        return ResponseModel(data=group)
    async def get_group_by_id(self, group_id:str):
        group = await self.group_repository.get_group_by_id(group_id)
        if group:
            return ResponseModel(data=group)
        raise GroupException(message=GroupMessage.NOT_FOUND,code=GroupStatusCode.NOT_FOUND)

    async def get_list_group(self, filters: FilterGroupModel):
        groups, total = await self.group_repository.get_list_of_groups(filters)
        return ResponsePaginatedModel(data=groups, total=total,offset=filters.offset)