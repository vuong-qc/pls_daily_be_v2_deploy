from beanie import PydanticObjectId
from beanie.operators import Set, In, LTE, GTE, And, NotIn

from src.models.work_item.work_item_document import WorkItemDocument
from src.models.user.user_document import UserDocument
from src.models.document_item.document_item_document import DocumentItem
from src.models.document_result.document_result_document import DocumentResult  # TODO: sửa path đúng thực tế
from src.repositories.document_item.document_item_repository import DocumentItemRepository
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem


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
            filter_dump.update(In(DocumentItem.type, filters.type))
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
        self._build_filter(filters, filter_dump)
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