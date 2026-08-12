from beanie import PydanticObjectId

from src.models.user.user_document import UserDocument
from src.models.work_item.work_item_document import WorkItemDocument
from src.models.document_item.document_item_document import DocumentItem
from src.repositories.plan.plan_repository import PlanRepository
from src.models.plan.plan_document import PlanDocument
from src.models.plan.request.filter_plan_model import FilterPlanModel
from beanie.operators import Set, And, LTE, GTE, In

class BeaniePlanRepository(PlanRepository):
    async def create_plan(self, data: dict)-> PlanDocument:
        doc = PlanDocument(**data)
        await self._add_link_plan(data,doc)
        await doc.insert()
        return await PlanDocument.find_one(PlanDocument.id == doc.id, fetch_links=True)
    async def update_plan(self, plan_id: str, data: dict)-> PlanDocument|None:
        plan = await PlanDocument.get(plan_id)
        if plan:
            await self._add_link_plan(data,plan)
            await plan.save()
            await plan.update(Set(data))
            return await PlanDocument.find_one(PlanDocument.id == plan.id, fetch_links=True)
        return None
    async def delete_plan(self, plan_id: str):
        plan = await PlanDocument.get(plan_id)
        if plan:
            await plan.delete()
    async def get_plan_by_id(self, plan_id: str) -> PlanDocument| None:
        return await PlanDocument.get(plan_id)
    async def get_list_plan(self, filters: FilterPlanModel) -> tuple[list[PlanDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop('offset', 0)
        limit = filter_dump.pop('limit', 10)
        start_date = filter_dump.pop('start_date', None)
        end_date = filter_dump.pop('end_date', None)
        if start_date and end_date:
            filter_dump.update(
                And(LTE(PlanDocument.date,end_date),
                    GTE(PlanDocument.date,start_date))
            )
        elif start_date:
            filter_dump.update(
                GTE(PlanDocument.date,start_date)
            )
        elif end_date:
            filter_dump.update(
                LTE(PlanDocument.date,end_date)
            )
        if filters.user_ids:
            filter_dump.update(
                In(PlanDocument.user_id, filter_dump.pop('user_ids', []))
            )

        query = PlanDocument.find(filter_dump, fetch_links=True)
        count = await query.count()
        list_plan = await query.skip(offset).limit(limit).to_list()
        return list_plan, count
    async def _add_link_plan(self, data: dict, plan: PlanDocument):
        user_id: str | bool = data.get('user_id', False)
        to_do: list[str] | bool = data.get("to_do", False)
        task: list[str] | bool = data.get("task", False)

        if type(user_id) is not bool:
            if user_id is None or not PydanticObjectId.is_valid(user_id):
                plan.user_model = None
            else:
                plan.user_model = UserDocument.model_construct(id=PydanticObjectId(user_id))

        if type(to_do) is not bool:
            if to_do == [] or to_do is None:
                plan.todo_model = []
            else:
                plan.todo_model = [
                    DocumentItem.model_construct(id=PydanticObjectId(to_do_item))
                    for to_do_item in to_do if PydanticObjectId.is_valid(to_do_item)
                ]
        if type(task) is not bool:
            if task == [] or task is None:
                plan.task_model = []
            else:
                plan.task_model = [
                    WorkItemDocument.model_construct(id=PydanticObjectId(task_item))
                    for task_item in task if PydanticObjectId.is_valid(task_item)
                ]