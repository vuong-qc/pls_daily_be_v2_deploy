from typing import Optional

from src.enums.work_item_type import WorkItemType
from src.models.work_item.request.filter_work_item import FilterWorkItemModel, ParentStatusCount
from src.models.project.response.project_response_model import ProjectResponse
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.work_item.work_item_document import WorkItemDocument, SprintTaskStatsResult
from beanie.operators import Set, In, RegEx, LTE, GTE, And, Or
from beanie import PydanticObjectId
from src.enums.task_priority_enum import TaskPriorityEnum
from src.enums.bug_type_enum import BugTypeEnum
from src.enums.bug_status_enum import BugStatusEnum
from datetime import datetime, timezone
from src.models.user.user_document import UserDocument
import re
import logging
logger = logging.getLogger(__name__)
DAY_MS = 24 * 60 * 60 * 1000
VN_OFFSET_MS = 7 * 60 * 60 * 1000  # UTC+7
BUG_TYPE_BUG = BugTypeEnum.BUG_TYPE_BUG.value
BUG_TYPE_FEEDBACK = BugTypeEnum.BUG_TYPE_FEEDBACK.value

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
        if not filters.status:
            filter_dump.pop("status", None)
        if filters.list_ids:
            filter_dump.update(
                In(WorkItemDocument.id, [PydanticObjectId(id) for id in filter_dump.pop('list_ids', [])]),
            )
        if filters.search:
            keyword = filter_dump.pop("search").strip().split()
            normalized = " ".join(keyword)
            escaped = re.escape(normalized)
            regex = f".*{escaped}.*"
            filter_dump.update(
                RegEx(WorkItemDocument.title, regex, "i")
            )
        if filters.handler_id:
            filter_dump.update(
                In(WorkItemDocument.handler_id, filters.handler_id)
            )
        if filters.owner_id:
            filter_dump.update(
                In(WorkItemDocument.owner_id, filters.owner_id)
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

        # ---- SỬA: gộp assigned_id + status + deadline vào chung 1 khối xử lý STORY ----
        # Lý do gộp: cả 3 field này đều là "field của task", không tồn tại (hoặc không đáng tin)
        # trên chính document STORY (story không có status, deadline/assigned_id thực chất nằm ở
        # task con: task.parent = story.id). Nên phải kiểm tra qua task con rồi suy ngược ra STORY,
        # thay vì AND thẳng field đó lên chính document STORY như code cũ.
        child_raw_query = {}  # dùng để distinct() tìm story_id qua task con
        non_story_exprs = []  # áp trực tiếp cho các type khác STORY (giữ nguyên hành vi cũ)

        if filters.assigned_id:
            filter_dump.pop("assigned_id", None)
            child_raw_query["assigned_id"] = {"$in": filters.assigned_id}
            non_story_exprs.append(In(WorkItemDocument.assigned_id, filters.assigned_id))

        if filters.status:
            status_values = filter_dump.pop("status")
            child_raw_query["status"] = {"$in": status_values}
            non_story_exprs.append(In(WorkItemDocument.status, status_values))

        if filters.deadline_end and filters.deadline_start:
            d_start = filter_dump.pop('deadline_start')
            d_end = filter_dump.pop('deadline_end')
            child_raw_query["deadline"] = {"$gte": d_start, "$lte": d_end}
            non_story_exprs.append(
                And(GTE(WorkItemDocument.deadline, d_start), LTE(WorkItemDocument.deadline, d_end))
            )
        elif filters.deadline_start:
            d_start = filter_dump.pop('deadline_start')
            child_raw_query["deadline"] = {"$gte": d_start}
            non_story_exprs.append(GTE(WorkItemDocument.deadline, d_start))
        elif filters.deadline_end:
            d_end = filter_dump.pop('deadline_end')
            child_raw_query["deadline"] = {"$lte": d_end}
            non_story_exprs.append(LTE(WorkItemDocument.deadline, d_end))

        has_story_type = bool(filters.type) and WorkItemType.STORY in filters.type
        filter_dump.pop("type", None)

        if child_raw_query and has_story_type:
            # Tìm các story có ÍT NHẤT 1 task con thoả toàn bộ điều kiện (assigned_id/status/deadline)
            motor_collection = WorkItemDocument.get_pymongo_collection()
            story_ids_raw = await motor_collection.distinct(
                "parent",
                {**child_raw_query, "parent": {"$ne": None}},
            )
            story_ids = [
                PydanticObjectId(pid) if not isinstance(pid, PydanticObjectId) else pid
                for pid in story_ids_raw
            ]

            or_conditions = []
            other_types = [t for t in filters.type if t != WorkItemType.STORY]
            if other_types:
                # Nhánh các type khác STORY: áp điều kiện trực tiếp lên chính document như cũ
                or_conditions.append(
                    And(In(WorkItemDocument.type, other_types), *non_story_exprs)
                )
            # Nhánh STORY: suy ra từ task con khớp điều kiện
            or_conditions.append(
                And(WorkItemDocument.type == WorkItemType.STORY, In(WorkItemDocument.id, story_ids))
            )
            filter_dump.update(Or(*or_conditions))
            type_handled_in_or = True
        else:
            # Không liên quan STORY -> giữ hành vi cũ, áp thẳng lên document
            for expr in non_story_exprs:
                filter_dump.update(expr)
            type_handled_in_or = False
        # ---- HẾT PHẦN SỬA ----

        if filters.type and not type_handled_in_or:
            filter_dump.update(
                In(WorkItemDocument.type, filters.type)
            )
        if filters.priority:
            filter_dump.update(
                In(WorkItemDocument.priority, filters.priority)
            )
        if filters.group:
            filter_dump.update(
                In(WorkItemDocument.group, filters.group)
            )
        if filters.project:
            filter_dump.update(
                In(WorkItemDocument.project, filters.project)
            )
        if filters.sprint:
            filter_dump.update(
                In(WorkItemDocument.sprint, filters.sprint)
            )
        if filters.task:
            filter_dump.update(
                In(WorkItemDocument.task, filters.task)
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
                    "_id": {"parent": "$parent", "status": "$status", "deleted_at": None},
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
    def _build_time_buckets(self, start_time: int, end_time: int) -> list[dict]:
        """
        Chia [start_time, end_time] thành tối đa 7 bucket theo NGÀY LỊCH
        GIỜ VIỆT NAM (00:00 -> 23:59:59.999 giờ VN).
        - Số ngày <= 7  -> mỗi bucket đúng 1 ngày VN, số bucket = số ngày.
        - Số ngày > 7   -> chia đúng 7 bucket, mỗi bucket số ngày nguyên,
          không có bucket lẻ (vd 2.5 ngày). Ngày dư dồn vào các bucket cuối.
        """
        if end_time <= start_time:
            return [{"start_time": start_time, "end_time": end_time}]

        vn_start_day = self._vn_day_start(start_time)
        vn_end_day = self._vn_day_start(end_time)

        # Tổng số ngày lịch VN nằm trong khoảng (tính cả ngày bắt đầu và kết thúc)
        total_days = max(1, round((vn_end_day - vn_start_day) / DAY_MS) + 1)
        num_buckets = min(total_days, 7)

        base_days = total_days // num_buckets
        remainder = total_days % num_buckets

        # remainder bucket cuối có (base_days + 1) ngày, còn lại base_days ngày
        bucket_day_counts = [base_days] * (num_buckets - remainder) + [
            base_days + 1
        ] * remainder

        buckets = []
        cursor_day_start = vn_start_day  # mốc 00:00 VN của ngày đầu tiên
        for idx, days in enumerate(bucket_day_counts):
            bucket_start = start_time if idx == 0 else cursor_day_start
            next_day_start = cursor_day_start + days * DAY_MS
            bucket_end = end_time if idx == len(bucket_day_counts) - 1 else next_day_start
            buckets.append({"start_time": bucket_start, "end_time": bucket_end})
            cursor_day_start = next_day_start

        return buckets
    def _build_common_filter(self, filters: FilterWorkItemModel) -> dict:
        query: dict = {"deleted_at": {"$eq": None}}

        if filters.project:
            query["project"] = {"$in": filters.project}
        if filters.group:
            query["group"] = {"$in": filters.group}
        if filters.sprint:
            query["sprint"] = {"$in": filters.sprint}
        if filters.owner_id:
            query["owner_id"] = {"$in": filters.owner_id}
        if filters.assigned_id:
            query["assigned_id"] = {"$in": filters.assigned_id}
        if filters.handler_id:
            query["handler_id"] = {"$in": filters.handler_id}
        if filters.is_in_sprint is not None:
            query["is_in_sprint"] = filters.is_in_sprint
        if filters.list_ids:
            query["_id"] = {"$in": [PydanticObjectId(i) for i in filters.list_ids]}
        if filters.search:
            query["title"] = {"$regex": filters.search, "$options": "i"}

        return query

    async def _aggregate_bug_stats(
        self,
        base_match: dict,
        extra_match: Optional[dict],
        buckets: list[dict],
    ) -> dict:
        match_stage = dict(base_match)
        if extra_match:
            match_stage.update(extra_match)

        facet: dict = {
            "total": [{"$count": "count"}],
            "total_resolve": [
                {"$match": {"status": BugStatusEnum.VERIFIED.value}},
                {"$count": "count"},
            ],
        }

        for idx, bucket in enumerate(buckets):
            upper_bound = (
                bucket["end_time"] + 1
                if idx == len(buckets) - 1
                else bucket["end_time"]
            )
            facet[f"bucket_{idx}"] = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": bucket["start_time"],
                            "$lt": upper_bound,
                        }
                    }
                },
                {"$count": "count"},
            ]

        pipeline = [{"$match": match_stage}, {"$facet": facet}]

        collection = WorkItemDocument.get_pymongo_collection()
        cursor = await collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        data = result[0] if result else {}

        def _count(key: str) -> int:
            arr = data.get(key) or []
            return arr[0]["count"] if arr else 0

        time_values = [
            {
                "start_time": bucket["start_time"],
                "end_time": bucket["end_time"],
                "value": _count(f"bucket_{idx}"),
            }
            for idx, bucket in enumerate(buckets)
        ]

        return {
            "total": _count("total"),
            "total_resolve": _count("total_resolve"),
            "time": time_values,
        }

    def _vn_day_start(self, ts_ms: int) -> int:
        """
        Trả về mốc epoch (ms, UTC) tương ứng với 00:00:00 giờ VN
        của ngày chứa ts_ms.
        """
        shifted = ts_ms + VN_OFFSET_MS
        day_start_shifted = shifted - (shifted % DAY_MS)
        return day_start_shifted - VN_OFFSET_MS
    async def statistic_bug(self, filters: FilterWorkItemModel) -> dict:
        """
        Thống kê bug: summary (tổng quan), critical_bug (priority FTF),
        feedback (bug_type FEEDBACK).
        """
        common_filter = self._build_common_filter(filters)
        common_filter["type"] = WorkItemType.BUG.value  # chỉ lấy work item loại BUG

        end_time = filters.end or int(datetime.now(timezone.utc).timestamp() * 1000)

        if filters.start is not None:
            start_time = filters.start
        else:
            # Không truyền start -> lấy created_at nhỏ nhất trong tập đã match
            # các filter khác (chưa có created_at) để làm mốc bắt đầu.
            start_time = await self._get_earliest_created_at(common_filter, end_time)

        common_filter["created_at"] = {"$gte": start_time, "$lte": end_time}

        buckets = self._build_time_buckets(start_time, end_time)

        summary = await self._aggregate_bug_stats(common_filter, None, buckets)

        critical_bug = await self._aggregate_bug_stats(
            common_filter,
            {
                # "bug_type": BUG_TYPE_BUG,
                "priority": TaskPriorityEnum.FTF.value},
            buckets,
        )

        feedback = await self._aggregate_bug_stats(
            common_filter,
            {"bug_type": BUG_TYPE_FEEDBACK},
            buckets,
        )

        return {
            "summary": summary,
            "critical_bug": critical_bug,
            "feedback": feedback,
        }

    async def _get_earliest_created_at(self, base_filter: dict, fallback: int) -> int:
        """
        Lấy created_at nhỏ nhất trong tập document match base_filter
        (base_filter lúc này chưa có key created_at).
        Nếu không có document nào, trả về fallback (thường là end_time)
        để tránh bucket rỗng/âm.
        """
        collection = WorkItemDocument.get_pymongo_collection()
        cursor = await collection.aggregate([
            {"$match": base_filter},
            {"$group": {"_id": None, "min_created_at": {"$min": "$created_at"}}},
        ])
        result = await cursor.to_list(length=1)

        if not result or result[0].get("min_created_at") is None:
            return fallback

        return result[0]["min_created_at"]
    async def count_total_tasks_in_sprint(self, filters: FilterWorkItemModel) -> int:
        """
        Đếm tổng số TASK (phẳng) thuộc 1 sprint, dựa trên FilterWorkItemModel:
        - TASK có parent = filters.parent (task lẻ, không nằm trong story)
        - TASK có parent = story_id, với story đó có parent = filters.parent
        filters.parent bắt buộc phải có (chính là sprint_id).
        Các field khác (status, deadline_start/end, priority, assigned_id) dùng để lọc task.
        """
        if not filters.parent:
            return 0

        motor_collection = WorkItemDocument.get_pymongo_collection()

        # B1: lấy id các STORY thuộc sprint này
        story_ids_raw = await motor_collection.distinct(
            "_id",
            {"parent": filters.parent, "type": WorkItemType.STORY, "deleted_at": None},
        )
        story_ids = [str(sid) for sid in story_ids_raw]

        # B2: build điều kiện áp cho task, lấy trực tiếp từ filters
        task_conditions: dict = {"type": WorkItemType.TASK, "deleted_at": None}
        if filters.status:
            task_conditions["status"] = {"$in": filters.status}
        if filters.priority:
            task_conditions["priority"] = {"$in": filters.priority}
        if filters.assigned_id:
            task_conditions["assigned_id"] = {"$in": filters.assigned_id}
        if filters.deadline_start and filters.deadline_end:
            task_conditions["deadline"] = {"$gte": filters.deadline_start, "$lte": filters.deadline_end}
        elif filters.deadline_start:
            task_conditions["deadline"] = {"$gte": filters.deadline_start}
        elif filters.deadline_end:
            task_conditions["deadline"] = {"$lte": filters.deadline_end}

        # B3: parent phải thuộc {sprint_id} hợp {story_ids}
        parent_candidates = [filters.parent] + story_ids
        query = {**task_conditions, "parent": {"$in": parent_candidates}}

        count = await motor_collection.count_documents(query)
        return count

    def _build_bucket_switch_branches(self, buckets: list[dict]) -> list[dict]:
        """
        Tạo các branch cho $switch để map mỗi document vào đúng bucket_idx
        dựa trên created_at. Bucket cuối dùng $lte để không bị rớt record
        có created_at == end_time.
        """
        branches = []
        for idx, bucket in enumerate(buckets):
            branches.append({
                "case": {
                    "$and": [
                        {"$gte": ["$created_at", bucket["start_time"]]},
                        {"$lte": ["$created_at", bucket["end_time"]]},
                    ]
                },
                "then": idx,
            })
        return branches

    def _build_match_stage(
            self,
            type_: Optional[list[str]],
            assigned_ids: Optional[list[str]],
            parent: Optional[str],
            status: Optional[list[str]],
            start_time: int,
            end_time: int,
    ) -> dict:
        match_stage: dict = {
            "created_at": {"$gte": start_time, "$lte": end_time},
        }
        if type_:
            match_stage["type"] = {"$in": type_}
        if assigned_ids:
            match_stage["assigned_id"] = {"$in": assigned_ids}
        if parent:
            match_stage["parent"] = parent
        if status:
            match_stage["status"] = {"$in": status}
        return match_stage

    async def count_by_time_buckets(
            self,
            filters: FilterWorkItemModel
    ) -> dict:
        """
        Trả về số lượng work item theo từng bucket thời gian.
        Kết quả: [{"start_time": ..., "end_time": ..., "count": ...}, ...]
        """
        end_time = filters.end or int(datetime.now(timezone.utc).timestamp() * 1000)
        start_time = filters.start or (end_time - 30 * DAY_MS)
        buckets = self._build_time_buckets(start_time, end_time)
        branches = self._build_bucket_switch_branches(buckets)
        match_stage = self._build_match_stage(filters.type, filters.assigned_id, filters.parent, filters.status,start_time, end_time)

        pipeline = [
            {"$match": match_stage},
            {
                "$addFields": {
                    "bucket_idx": {
                        "$switch": {"branches": branches, "default": None}
                    }
                }
            },
            {"$match": {"bucket_idx": {"$ne": None}}},
            {"$group": {"_id": "$bucket_idx", "count": {"$sum": 1}}},
        ]

        cursor = await WorkItemDocument.get_pymongo_collection().aggregate(pipeline)
        results = await cursor.to_list(None)
        count_map = {r["_id"]: r["count"] for r in results}

        # return [
        #     {
        #         "start_time": bucket["start_time"],
        #         "end_time": bucket["end_time"],
        #         "count": count_map.get(idx, 0),
        #     }
        #     for idx, bucket in enumerate(buckets)
        # ]

        response = [
            {
                "start_time": bucket["start_time"],
                "end_time": bucket["end_time"],
                "total_point": count_map.get(idx, 0),
            }
            for idx, bucket in enumerate(buckets)
        ]
        total = 0
        for idx, bucket in enumerate(buckets):
            total += count_map.get(idx, 0)

        return {
            "total": total,
            "time": response
        }

    async def sum_point_by_time_buckets(
            self,
            filters: FilterWorkItemModel
    ) -> dict:
        """
        Trả về tổng point của work item theo từng bucket thời gian.
        Kết quả: [{"start_time": ..., "end_time": ..., "total_point": ...}, ...]
        """
        end_time = filters.end or int(datetime.now(timezone.utc).timestamp() * 1000)
        start_time = filters.start or (end_time - 30 * DAY_MS)
        buckets = self._build_time_buckets(start_time, end_time)
        branches = self._build_bucket_switch_branches(buckets)
        match_stage = self._build_match_stage(filters.type, filters.assigned_id, filters.parent, filters.status,start_time, end_time)

        pipeline = [
            {"$match": match_stage},
            {
                "$addFields": {
                    "bucket_idx": {
                        "$switch": {"branches": branches, "default": None}
                    }
                }
            },
            {"$match": {"bucket_idx": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$bucket_idx",
                    "total_point": {"$sum": {"$ifNull": ["$point", 0]}},
                }
            },
        ]

        cursor = await WorkItemDocument.get_pymongo_collection().aggregate(pipeline)
        results = await cursor.to_list(None)
        point_map = {r["_id"]: r["total_point"] for r in results}
        response = [
            {
                "start_time": bucket["start_time"],
                "end_time": bucket["end_time"],
                "total_point": point_map.get(idx, 0),
            }
            for idx, bucket in enumerate(buckets)
        ]
        total = 0
        for idx, bucket in enumerate(buckets):
            total += point_map.get(idx, 0)

        return {
            "total": total,
            "time": response
                }