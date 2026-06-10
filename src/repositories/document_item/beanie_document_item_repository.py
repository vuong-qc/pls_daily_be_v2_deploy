from src.models.document_item.document_item_document import DocumentItem
from src.repositories.document_item.document_item_repository import DocumentItemRepository
from beanie.operators import Set, In
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem


class BeanieDocumentItemRepository(DocumentItemRepository):
    async def create_document(self, data: dict) -> DocumentItem:
        document = DocumentItem(**data)
        await document.insert()
        return document
    async def update_document(self, document_id: str, data: UpdateDocumentItem) -> DocumentItem|None:
        document = await DocumentItem.get(document_id)
        if document:
            await document.update(Set(data.model_dump(exclude_unset=True)))
            return document
        return None
    async def delete_document(self, document_id: str) -> None:
        document = await DocumentItem.get(document_id)
        if document:
            await document.delete()
    async def get_document_item(self, document_id: str) -> DocumentItem|None:
        document = await DocumentItem.get(document_id)
        return document

    async def get_list_document_items(self, filters: FilterDocumentItem) ->tuple[list[DocumentItem], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop('offset',0)
        limit = filter_dump.pop('limit',10)
        if filters.type:
            filter_dump.update(
                In(DocumentItem.type, filters.type),
            )
        if filters.parent_type:
            filter_dump.update(
                In(DocumentItem.parent_type, filters.parent_type),
            )
        query = DocumentItem.find(filter_dump)
        count = await query.count()

        list_document = await query.skip(offset).limit(limit).sort("-date_time").to_list()
        return list_document, count