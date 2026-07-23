from typing import Optional

from src.enums.work_item_type import WorkItemType
from src.models.work_item.request.filter_work_item import FilterWorkItemModel, ParentStatusCount
from src.models.project.response.project_response_model import ProjectResponse
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.work_item.work_item_document import WorkItemDocument, SprintTaskStatsResult
from beanie.operators import Set, In, RegEx, LTE, GTE, And, Or
from beanie import PydanticObjectId
from src.models.user.user_document import UserDocument
import logging
logger = logging.getLogger(__name__)

class BeanieWorkItemRepository(WorkItemRepository):
    async def create_work_item(self, data: dict):
        project = WorkItemDocument(**data)
        await self._add_link_document(data, project)
        await project.insert()
        created_project = await WorkItemDocument.find_one(WorkItemDocument.id == PydanticObjectId(project.id),fetch_links=True)
        return created_project

    async def update_work_item(self, project_id:str, data: dict) -> ProjectResponse|None:
        project = await WorkItemDocument.get(project_id)
        if project:
            # clear dump data
            data.pop('order_type',None)
            data.pop('next_order',None)
            data.pop('prev_order',None)
            if project.type == WorkItemType.BACKLOG:
                return await WorkItemDocument.find_one(WorkItemDocument.id == PydanticObjectId(project.id),fetch_links=True)
            await self._add_link_document(data, project)
            await project.save()
            await project.update(Set(data))
            # print("data", data)
            # print(project)
            updated_project = await WorkItemDocument.find_one(WorkItemDocument.id == PydanticObjectId(project.id),fetch_links=True)
            return updated_project
        return None
    async def delete_work_item(self, project_id:str):
        project = await WorkItemDocument.get(project_id)
        if project:
            if project.type == WorkItemType.BACKLOG:
                return
            await project.delete()
    async def get_list_work_items(self, filters: FilterWorkItemModel) ->tuple[list[WorkItemDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        logger.info('filter work item before apply update: %s', filter_dump)

        offset = filter_dump.pop("offset",0)
        limit = filter_dump.pop("limit",10)
        await self._update_query_by_form(filters, filter_dump)

        logger.info('filter work item: %s', filter_dump)

        query = WorkItemDocument.find(filter_dump,
                                      fetch_links=True,
                                      nesting_depth=1
                                      )
        count = await query.count()
        results = await query.skip(offset).limit(limit).to_list()
        logger.info("test link doc: %s", results)
        for link in results:
            print("project",link)

        # res = [ProjectResponse.model_validate(item.model_dump(mode="json")) for item in results]
        # print("test res",res)
        return results, count

    async def get_work_item_by_id(self, project_id:str):
        project = await WorkItemDocument.find_one(WorkItemDocument.id==PydanticObjectId(project_id), fetch_links=True, nesting_depth=1)
        if project:
            return project
        return None

    async def count_work_item(self, filters: FilterWorkItemModel) ->int:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset",0)
        limit = filter_dump.pop("limit",10)
        await self._update_query_by_form(filters, filter_dump)
        logger.info('filter work item for count: %s', filter_dump)
        query = WorkItemDocument.find(filter_dump)
        count = await query.count()
        return count
    async def get_children(self, parent_id:str, status: Optional[list[str]]= None, user_id: Optional[str]= None) ->list[WorkItemDocument]:
        filters = FilterWorkItemModel(offset=0, limit=10, parent=parent_id)

        if user_id:
            filters.assigned_id = [user_id]
        if status:
            filters.status = status
        filter_dump = filters.model_dump(exclude_unset=True)
        await self._update_query_by_form(filters, filter_dump)
        offset = filter_dump.pop("offset",0)
        limit = filter_dump.pop("limit",10)
        print("filter",filter_dump)
        query = WorkItemDocument.find(filter_dump,
                                      fetch_links=True,
                                      )
        children = await query.to_list()
        return children

    async def get_children_by_parents(self, parents: list[str], status: Optional[list[str]]= None, user_id: Optional[list[str]]= None):
        filters = FilterWorkItemModel(offset=0, limit=10)
        if user_id:
            filters.assigned_id = user_id
        if status:
            filters.status = status
        filter_dump = filters.model_dump(exclude_unset=True)
        filter_dump.update(
            In(WorkItemDocument.parent, parents)
        )
        offset = filter_dump.pop("offset",0)
        limit = filter_dump.pop("limit",10)
        print("filter",filter_dump)
        query = WorkItemDocument.find(filter_dump,
                                      fetch_links=True,
                                      )
        children = await query.to_list()
        return children
    async def _update_query_by_form(self, filters: FilterWorkItemModel, filter_dump: dict):
        if filters.type_order:
            filter_dump.pop("type_order")
        filter_dump.pop('is_today', None)
        # list_ids = filter_dump.pop('list_ids',[])
        if filters.list_ids:
            filter_dump.update(
                In(WorkItemDocument.id, [PydanticObjectId(id) for id in filter_dump.pop('list_ids',[])]),
            )
        if filters.search:
            filter_dump.update(
                RegEx(WorkItemDocument.title, filter_dump.pop("search"),"i")
            )
        if filters.handler_id:
            filter_dump.update(
                In(WorkItemDocument.handler_id,filters.handler_id)
            )
        if filters.owner_id:
            filter_dump.update(
                In(WorkItemDocument.owner_id,filters.owner_id)
            )
        if filters.assigned_id is None:
            filter_dump.pop("assigned_id", None)
        if filters.start and filters.end:
            filter_dump.update(
                And(
                    GTE(WorkItemDocument.created_at, filter_dump.pop("start")),
                    LTE(WorkItemDocument.created_at, filter_dump.pop("end"))
                )
            )
        elif filters.start:
            filter_dump.update(
                    GTE(WorkItemDocument.created_at, filter_dump.pop("start")),
            )
        elif filters.end:
            filter_dump.update(
                    LTE(WorkItemDocument.created_at, filter_dump.pop("end")),
            )
        # if filters.assigned_id:
        #     filter_dump.update(
        #         In(WorkItemDocument.assigned_id,filters.assigned_id)
        #     )
        # ---- assigned_id: xử lý riêng case STORY ----
        if filters.assigned_id:
            filter_dump.pop("assigned_id", None)  # bỏ key mặc định để tự build $or
            assigned_ids = filters.assigned_id
            or_conditions = [In(WorkItemDocument.assigned_id, assigned_ids)]

            if filters.type and WorkItemType.STORY in filters.type:
                # Lấy các parent (story id) có task con đang assign đúng người
                motor_collection = WorkItemDocument.get_pymongo_collection()
                story_ids_raw = await motor_collection.distinct(
                    "parent",
                    {
                        "assigned_id": {"$in": assigned_ids},
                        "parent": {"$ne": None},
                    },
                )
                if story_ids_raw:
                    story_ids = [
                        PydanticObjectId(pid) if not isinstance(pid, PydanticObjectId) else pid
                        for pid in story_ids_raw
                    ]
                    or_conditions.append(
                        And(
                            WorkItemDocument.type == WorkItemType.STORY,
                            In(WorkItemDocument.id, story_ids),
                        )
                    )

            filter_dump.update(Or(*or_conditions))
        # ------------------------------------------------

        if filters.type:
            filter_dump.update(
                In(WorkItemDocument.type,filters.type)
            )
        if filters.status:
            filter_dump.update(
                In(WorkItemDocument.status,filters.status)
            )
        if filters.priority:
            filter_dump.update(
                In(WorkItemDocument.priority, filters.priority)
            )
        if filters.group:
            filter_dump.update(
                In(WorkItemDocument.group,filters.group)
            )
        if filters.project:
            filter_dump.update(
                In(WorkItemDocument.project,filters.project)
            )
        if filters.sprint:
            filter_dump.update(
                In(WorkItemDocument.sprint,filters.sprint)
            )
        if filters.task:
            filter_dump.update(
                In(WorkItemDocument.task,filters.task)
            )

        if filters.deadline_end and filters.deadline_start:
            filter_dump.update(
                And(
                    GTE(WorkItemDocument.deadline, filter_dump.pop('deadline_start')),
                    LTE(WorkItemDocument.deadline, filter_dump.pop('deadline_end'))
                )
            )

        elif filters.deadline_start:
            filter_dump.update(
                GTE(WorkItemDocument.deadline,filter_dump.pop('deadline_start'))
            )
        elif filters.deadline_end:
            filter_dump.update(
                LTE(WorkItemDocument.deadline,filter_dump.pop('deadline_end'))
            )


    async def _add_link_document(self, data: dict, project: WorkItemDocument):
        handler_id: list[str] | bool = data.get("handler_id", False)
        # print("handler_id",handler_id)
        # getattr(data,"owner_id", False)
        assigned_id: list[str] | bool =  data.get("assigned_id", False)
        print("assign_id",assigned_id)
        parent_id: str | bool = data.get('parent', False)
        if parent_id:
            check_work_item = await WorkItemDocument.get(parent_id)
            if check_work_item:
                project.parent_model = WorkItemDocument.model_construct(id=PydanticObjectId(parent_id))
        if type(handler_id) is not bool:
            if handler_id == [] or handler_id is None:
                project.handler = []
            else:
                project.handler = [
                    UserDocument.model_construct(id=PydanticObjectId(uid))
                    for uid in data['handler_id']
                ]
        # print("check update data",data)
        if data.get("owner_id"):
            project.owner = UserDocument.model_construct(id=PydanticObjectId(data['owner_id']))

        if type(assigned_id) is not bool:
            if assigned_id == [] or assigned_id is None:
                project.assignee = []
            else:
                project.assignee = [
                    UserDocument.model_construct(id=PydanticObjectId(uid))
                    for uid in data['assigned_id']
                ]
        # print("check work item", project)

    async def statistic_task(self, sprint_ids:list[str], item_type:str, target_status: list[str]) -> SprintTaskStatsResult | None:
        pipeline = [
            # Bước 1: Tìm chính xác Sprint
            {
                "$match": {
                    "type": "SPRINT",
                    "_id": {
                        "$in": [PydanticObjectId(id) for id in sprint_ids]
                    }
                }
            },

            # Bước 2: Tìm tất cả STORY thuộc về Sprint này
            {
                "$lookup": {
                    "from": WorkItemDocument.get_collection_name(),
                    "let": {"sprint_id_str": {"$toString": "$_id"}},  # Ép kiểu ID của sprint sang string
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$type", "STORY"]},
                                        {"$eq": ["$parent", "$$sprint_id_str"]}
                                    ]
                                }
                            }
                        },
                        {"$project": {"_id": 1}}  # Chỉ lấy _id của Story để cho nhẹ
                    ],
                    "as": "stories"
                }
            },

            # Bước 3: Gộp ID của Sprint và ID của các Story thành 1 mảng danh sách các parent hợp lệ
            {
                "$addFields": {
                    "parent_ids_to_search": {
                        "$concatArrays": [
                            [{"$toString": "$_id"}],  # Thêm ID của Sprint (chuyển sang string)
                            {
                                "$map": {
                                    "input": "$stories",
                                    "as": "story",
                                    "in": {"$toString": "$$story._id"}  # Lấy ID của từng Story (chuyển sang string)
                                }
                            }
                        ]
                    }
                }
            },

            # Bước 4: Tìm TẤT CẢ Task có parent nằm trong mảng danh sách vừa tạo
            {
                "$lookup": {
                    "from": WorkItemDocument.get_collection_name(),
                    "let": {"parent_ids": "$parent_ids_to_search"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$type", item_type]},  # item_type truyền vào là "TASK"
                                        {"$in": ["$parent", "$$parent_ids"]}
                                        # Task thuộc trực tiếp Sprint hoặc thuộc Story
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "all_tasks"
                }
            },

            # Bước 5: Đếm tổng số lượng
            {
                "$project": {
                    "_id": 1,
                    "total_tasks": {"$size": "$all_tasks"},
                    "target_status_tasks": {
                        "$size": {
                            "$filter": {
                                "input": "$all_tasks",
                                "as": "task",
                                "cond": {"$in": ["$$task.status", target_status]}
                            }
                        }
                    }
                }
            }
        ]

        result = await WorkItemDocument.aggregate(
            pipeline,
            projection_model=SprintTaskStatsResult
        ).to_list(length=1)

        return result[0] if result else None

    async def filter_work_item_for_order(self, filters: FilterWorkItemModel) ->list[WorkItemDocument]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", 0)
        limit = filter_dump.pop("limit", 10)
        await self._update_query_by_form(filters, filter_dump)
        query = WorkItemDocument.find(filter_dump, fetch_links=True)
        list_work_item = await query.to_list()
        return list_work_item
    async def update_many(self, list_ids:list[str], data: dict):
        list_object_id = [ PydanticObjectId(id) for id in list_ids ]
        query = In(WorkItemDocument.id, list_object_id)
        await WorkItemDocument.find(query).update(Set(data))
        return

    async def count_items_by_parent_status(
            self,
            parents: list[str],
            statuses: list[str],
    ) -> dict[str, dict[str, int]]:
        pipeline = [
            {
                "$group": {
                    "_id": {"parent": "$parent", "status": "$status"},
                    "count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "parent": "$_id.parent",
                    "status": "$_id.status",
                    "count": 1,
                }
            },
        ]

        results = await WorkItemDocument.find(
            In(WorkItemDocument.parent,parents),  # optional, để tận dụng index sớm hơn (pre-filter)
            In(WorkItemDocument.status,statuses)
        ).aggregate(pipeline, projection_model=ParentStatusCount).to_list()
        # gom về dict: {parent: {status: count}}
        out: dict[str, dict[str, int]] = {p: {s: 0 for s in statuses} for p in parents}
        for r in results:
            out.setdefault(r.parent, {})[r.status] = r.count

        return out

    async def count_point(self, filters: FilterWorkItemModel) ->float:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", 0)
        limit = filter_dump.pop("limit", 10)
        await self._update_query_by_form(filters, filter_dump)

        sum_point = await WorkItemDocument.find(filter_dump).sum(f"{WorkItemDocument.point}")
        return  float(sum_point or 0)