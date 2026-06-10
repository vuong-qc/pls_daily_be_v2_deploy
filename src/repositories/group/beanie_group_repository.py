from src.models.group.group_document import GroupDocument
from src.models.group.response.group_reponse_model import GroupResponse
from src.repositories.group.group_repository import GroupRepository
from src.models.group.request.filter_group_model import FilterGroupModel
from beanie.operators import Set, In, RegEx
import re
class BeanieGroupRepository(GroupRepository):
    async def create_group(self, data: dict) ->GroupResponse:
        group = GroupDocument(**data)
        await group.insert()
        safe_data = group.model_dump(mode="json")
        return GroupResponse(**safe_data)
    async def get_group_by_id(self, group_id: str) -> GroupResponse|None:
        group = await GroupDocument.get(group_id)
        if group:
            return GroupResponse(**group.model_dump(mode="json"))
        return None

    async def update_group(self, group_id: str, data: dict) ->GroupResponse|None:
        group = await GroupDocument.get(group_id)
        if group:
            await group.update(Set(data))
            safe_data = group.model_dump(mode="json")
            return GroupResponse(**safe_data)
        return None
    async def delete_group(self, group_id: str):
        # soft delete -> set is_deleted = true
        group = await GroupDocument.get(group_id)
        if group:
            await group.delete()

    async def get_list_of_groups(self, filters: FilterGroupModel) -> tuple[list[GroupResponse],int]:
        data_dump = filters.model_dump(exclude_unset=True)
        offset = data_dump.pop("offset",0)
        limit = data_dump.pop("limit",10)
        if filters.type:
            data_dump.update(In(GroupDocument.type,filters.type))
        if filters.search:
            data_dump.update(RegEx(GroupDocument.name,data_dump.pop("search"),"i"))
        query = GroupDocument.find(data_dump)
        count = await query.count()
        print("query:",data_dump)
        list_group = await query.skip(offset).limit(limit).to_list()
        # if can t convert -> change
        result = [GroupResponse.model_validate(item.model_dump(mode="json")) for item in list_group]
        return result, count