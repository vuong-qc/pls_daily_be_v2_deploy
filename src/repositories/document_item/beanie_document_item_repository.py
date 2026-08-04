from beanie import PydanticObjectId
from beanie.operators import Set, In, LTE, GTE, And, NotIn

from src.models.work_item.work_item_document import WorkItemDocument
from src.models.user.user_document import UserDocument
from src.models.document_item.document_item_document import DocumentItem
from src.models.document_result.document_result_document import DocumentResult  # TODO: sửa path đúng thực tế
from src.repositories.document_item.document_item_repository import DocumentItemRepository
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem
from datetime import datetime, timezone
from typing import Optional

DAY_MS = 24 * 60 * 60 * 1000
VN_OFFSET_MS = 7 * 60 * 60 * 1000  # UTC+7
class BeanieDocumentItemRepository(DocumentItemRepository):
    async def create_document(self, data: dict) -> DocumentItem:
        document = DocumentItem(**data)
        await self._add_link_document_item(data, document)
        await document.insert()
        return await DocumentItem.find_one(DocumentItem.id == document.id, fetch_links=True, nesting_depth=1)

    async def update_document(self, document_id: str, data: UpdateDocumentItem) -> DocumentItem | None:
        document = await DocumentItem.get(document_id)
        if document:
            await self._add_link_document_item(data.model_dump(exclude_unset=True), document)
            await document.save()
            await document.update(Set(data.model_dump(exclude_unset=True)))

            return await DocumentItem.find_one(DocumentItem.id == document.id, fetch_links=True)

        return None

    async def delete_document(self, document_id: str) -> None:
        document = await DocumentItem.get(document_id)
        if document:
            await document.delete()

    async def get_document_item(self, document_id: str) -> DocumentItem | None:
        return await DocumentItem.find_one(DocumentItem.id == PydanticObjectId(document_id), fetch_links=True)

    async def get_list_document_items(self, filters: FilterDocumentItem) -> tuple[list[DocumentItem], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop('offset', 0)
        limit = filter_dump.pop('limit', 10)

        is_closed = filter_dump.pop('is_closed', None)
        match_stage = self._build_match(filters, filter_dump)

        pipeline: list[dict] = []

        # Join sang document_result CHỈ khi cần lọc is_closed
        if is_closed is not None:
            pipeline.append({
                "$lookup": {
                    "from": DocumentResult.get_collection_name(),  # "document_result"
                    "let": {"item_id": {"$toString": "$_id"}},
                    "pipeline": [
                        {"$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$parent_id", "$$item_id"]},
                                    {"$eq": ["$is_closed", is_closed]},
                                ]
                            }
                        }}
                    ],
                    "as": "matched_results",
                }
            })
            # match thì giữ lại, không match thì loại (results rỗng)
            pipeline.append({"$match": {"matched_results": {"$ne": []}}})

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.append({"$sort": {"date_time": 1}})
        pipeline.append({
            "$facet": {
                "data": [
                    {"$skip": offset},
                    {"$limit": limit},
                    {"$project": {"_id": 1}},
                ],
                "count": [{"$count": "total"}],
            }
        })

        result = await DocumentItem.aggregate(pipeline).to_list()
        print("pipeline", pipeline)
        print("result", result)
        facet = result[0] if result else {"data": [], "count": []}

        ids = [d["_id"] for d in facet.get("data", [])]
        count = facet["count"][0]["total"] if facet.get("count") else 0

        if not ids:
            return [], count

        # Hydrate lại bằng ODM để fetch_links (assignee_model, handler_model, task_model, sprint_model)
        list_document = await DocumentItem.find(
            In(DocumentItem.id, ids),
            fetch_links=True,
            nesting_depth=1,
        ).sort("+date_time").to_list()

        return list_document, count

    def _build_match(self, filters: FilterDocumentItem, filter_dump: dict) -> dict:
        """Xây dựng match dict thuần cho aggregation (không còn is_closed, offset, limit)."""
        no_object_id = filter_dump.pop('no_object_id', None)

        if filters.type:
            filter_dump.update(In(DocumentItem.type, [type_enum.value for type_enum in filters.type]))
        if filters.parent_type:
            filter_dump.update(In(DocumentItem.parent_type, filters.parent_type))
        if filters.group_id:
            filter_dump.update(In(DocumentItem.group_id, filters.group_id))

        if filters.object_id and no_object_id:
            filter_dump.update(
                And(
                    In(DocumentItem.object_id, filters.object_id),
                    NotIn(DocumentItem.object_id, no_object_id),
                )
            )
        elif filters.object_id:
            filter_dump.update(And(In(DocumentItem.object_id, filters.object_id)))
        elif filters.no_object_id:
            filter_dump.update(NotIn(DocumentItem.object_id, filters.no_object_id))

        start_deadline = filter_dump.pop('start_deadline', None)
        end_deadline = filter_dump.pop('end_deadline', None)
        if start_deadline and end_deadline:
            filter_dump.update(
                And(
                    GTE(DocumentItem.deadline, start_deadline),
                    LTE(DocumentItem.deadline, end_deadline),
                )
            )
        start_time = filter_dump.pop('start_time', None)
        end_time = filter_dump.pop('end_time', None)
        if start_time and end_time:
            filter_dump.update(
                And(
                    GTE(DocumentItem.date_time, start_time),
                    LTE(DocumentItem.date_time, end_time),
                )
            )
        filter_dump["deleted_at"]= None

        return filter_dump
    async def _add_link_document_item(self, data: dict, document: DocumentItem):
        handler: str | bool = data.get("handler", False)
        # print("handler_id",handler_id)
        # getattr(data,"owner_id", False)
        sprint: str | bool = data.get("sprint", False)
        task: str | bool = data.get("task", False)
        assignee: list[str] | bool = data.get("assignee", False)

        if type(handler) is not bool:
            if handler is None or not PydanticObjectId.is_valid(handler):
                document.handler_model = None
            else:
                document.handler_model = UserDocument.model_construct(id=PydanticObjectId(handler))


        if type(assignee) is not bool:
            if assignee == [] or assignee is None:
                document.assignee_model = []
            else:
                document.assignee_model = [
                    UserDocument.model_construct(id=PydanticObjectId(uid))
                    for uid in assignee if PydanticObjectId.is_valid(uid)
                ]

        if type(task) is not bool:
            if task is None or not PydanticObjectId.is_valid(task):
                document.task_model = None
            else:
                document.task_model = WorkItemDocument.model_construct(id=PydanticObjectId(task))

        if type(sprint) is not bool:
            if sprint is None or not PydanticObjectId.is_valid(sprint):
                document.sprint_model = None
            else:
                document.sprint_model = WorkItemDocument.model_construct(id=PydanticObjectId(sprint))

    async def copy_document_items(self, filters: FilterDocumentItem, new_object_id:str):
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop('offset', 0)
        limit = filter_dump.pop('limit', 10)
        self._build_match(filters, filter_dump)
        query = DocumentItem.find(filter_dump)
        list_document = await query.to_list()
        list_document_items = []
        for document in list_document:
            raw_data = document.model_dump()
            raw_data.pop('id', None)
            data = DocumentItem(**raw_data)
            data.object_id = new_object_id
            list_document_items.append(data)
        await DocumentItem.insert_many(list_document_items)
    def _vn_day_start(self, ts_ms: int) -> int:
        """
        Trả về mốc epoch (ms, UTC) tương ứng với 00:00:00 giờ VN
        của ngày chứa ts_ms.
        """
        shifted = ts_ms + VN_OFFSET_MS
        day_start_shifted = shifted - (shifted % DAY_MS)
        return day_start_shifted - VN_OFFSET_MS
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
    async def count_items_by_time_buckets(
            self,
            filters: FilterDocumentItem,
    ) -> dict:
        """
        Thống kê số lượng DocumentItem theo bucket thời gian (VN).
        Filter theo object_id, type và date_time trong [start_time, end_time].
        """

        end_time = filters.end_time or int(datetime.now(timezone.utc).timestamp() * 1000)
        filters.end_time = end_time

        filter_dump = filters.model_dump(exclude_unset=True)
        self._build_match(filters, filter_dump)
        filter_dump.pop('offset', 0)
        filter_dump.pop('limit', 10)

        if filters.start_time is None:
            start_time = await self._get_earliest_created_at(filter_dump, end_time)
            filters.start_time = start_time
            filter_dump = filters.model_dump(exclude_unset=True)
            filter_dump.pop('offset', 0)
            filter_dump.pop('limit', 10)
            self._build_match(filters, filter_dump)

        buckets = self._build_time_buckets(filters.start_time, end_time)

        facet_stage = self._build_facet_stage(buckets, f"{DocumentItem.date_time}")
        print("filter", filter_dump)
        pipeline = [
            {
                "$match": filter_dump,
            },
            {"$facet": facet_stage},
        ]

        result = await DocumentItem.aggregate(pipeline).to_list()
        raw = result[0] if result else {}
        res = self._map_bucket_result(buckets, raw)
        total = 0
        for item in res:
            total+= item["count"]
        return {"total": total, "time": res}

    async def count_completed_items_by_time_buckets(
            self,
            filters: FilterDocumentItem,

    ) -> dict:
        """
        Thống kê số lượng DocumentItem đã hoàn thành theo bucket thời gian.
        "Hoàn thành" = tồn tại DocumentResult có:
            - parent_id == str(document_item._id)
            - owner_id == object_id
            - check == True
            - updated_at trong [start_time, end_time]
        Bucket tính theo updated_at của DocumentResult (thời điểm hoàn thành),
        KHÔNG dùng date_time của DocumentItem để filter/bucket.
        """
        end_time = filters.end_time or int(datetime.now(timezone.utc).timestamp() * 1000)

        filter_dump = filters.model_dump(exclude_unset=True)
        self._build_match(filters, filter_dump)
        filter_dump.pop('offset', 0)
        filter_dump.pop('limit', 10)
        start_time = filters.start_time

        if start_time is None:
            start_time = await self._get_earliest_created_at(filter_dump, end_time)

        buckets = self._build_time_buckets(start_time, end_time)

        # change date_time to updated_at
        filter_dump.pop("start_time", None)
        filter_dump.pop("end_time", None)
        filter_dump.pop('offset', 0)
        filter_dump.pop('limit', 10)
        filter_dump.update(
            And(
                GTE(DocumentItem.updated_at, start_time),
                LTE(DocumentItem.updated_at, end_time),
            )
        )
        facet_stage = self._build_facet_stage(
            buckets, time_field=f"{DocumentItem.updated_at}"
        )
        print("filter done", filter_dump)
        pipeline = [
            {
                "$match": filter_dump
            },

            {"$facet": facet_stage},
        ]

        result = await DocumentItem.aggregate(pipeline).to_list()
        raw = result[0] if result else {}
        res = self._map_bucket_result(buckets, raw)
        total = 0
        for item in res:
            total += item["count"]
        return {"total": total, "time": res}

    @staticmethod
    def _build_facet_stage(buckets: list[dict], time_field: str) -> dict:
        facet_stage = {}
        for idx, bucket in enumerate(buckets):
            facet_stage[f"bucket_{idx}"] = [
                {
                    "$match": {
                        time_field: {
                            "$gte": bucket["start_time"],
                            "$lte": bucket["end_time"],
                        }
                    }
                },
                {"$count": "count"},
            ]
        return facet_stage

    @staticmethod
    def _map_bucket_result(buckets: list[dict], raw: dict) -> list[dict]:
        stats = []
        for idx, bucket in enumerate(buckets):
            bucket_result = raw.get(f"bucket_{idx}", [])
            count = bucket_result[0]["count"] if bucket_result else 0
            stats.append(
                {
                    "start_time": bucket["start_time"],
                    "end_time": bucket["end_time"],
                    "count": count,
                }
            )
        return stats

    async def _get_earliest_created_at(self, base_filter: dict, fallback: int) -> int:
        """
        Lấy created_at nhỏ nhất trong tập document match base_filter
        (base_filter lúc này chưa có key created_at).
        Nếu không có document nào, trả về fallback (thường là end_time)
        để tránh bucket rỗng/âm.
        """
        collection = DocumentItem.get_pymongo_collection()
        cursor = await collection.aggregate([
            {"$match": base_filter},
            {"$group": {"_id": None, "min_created_at": {"$min": "$date_time"}}},
        ])
        result = await cursor.to_list(length=1)

        if not result or result[0].get("min_created_at") is None:
            return fallback

        return result[0]["min_created_at"]