from beanie import PydanticObjectId

from src.models.work_item.work_item_document import WorkItemDocument
from src.models.user.user_document import UserDocument
from src.models.document_item.document_item_document import DocumentItem
from src.repositories.document_item.document_item_repository import DocumentItemRepository
from beanie.operators import Set, In
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem


class BeanieDocumentItemRepository(DocumentItemRepository):
    async def create_document(self, data: dict) -> DocumentItem:
        document = DocumentItem(**data)
        await self._add_link_document_item(data, document)
        await document.insert()
        return await DocumentItem.find_one(DocumentItem.id == document.id, fetch_links=True, nesting_depth=1)
    async def update_document(self, document_id: str, data: UpdateDocumentItem) -> DocumentItem|None:
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
    async def get_document_item(self, document_id: str) -> DocumentItem|None:
        return await DocumentItem.find_one(DocumentItem.id == PydanticObjectId(document_id), fetch_links=True)

    async def get_list_document_items(self, filters: FilterDocumentItem) ->tuple[list[DocumentItem], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop('offset',0)
        limit = filter_dump.pop('limit',10)
        self._build_filter(filters, filter_dump)
        query = DocumentItem.find(filter_dump, fetch_links=True, nesting_depth=1)
        count = await query.count()

        list_document = await query.skip(offset).limit(limit).sort("+date_time").to_list()
        return list_document, count
    def _build_filter(self, filters: FilterDocumentItem, filter_dump: dict):
        if filters.type:
            filter_dump.update(
                In(DocumentItem.type, filters.type),
            )
        if filters.parent_type:
            filter_dump.update(
                In(DocumentItem.parent_type, filters.parent_type),
            )
        if filters.group_id:
            filter_dump.update(
                In(DocumentItem.group_id, filters.group_id),
            )
        if filters.object_id:
            filter_dump.update(
                In(DocumentItem.object_id, filters.object_id),
            )
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
            data = DocumentItem(**document.model_dump())
            data.object_id = new_object_id
            list_document_items.append(data)
        await DocumentItem.insert_many(list_document_items)