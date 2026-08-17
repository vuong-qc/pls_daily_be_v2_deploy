from src.repositories.document_result.document_result_repository import DocumentResultRepository
from src.models.document_result.document_result_document import DocumentResult
from src.models.document_result.request.filter_document_result_model import FilterDocumentResult
from beanie.operators import Set, In

class BeanieDocumentResultRepository(DocumentResultRepository):
    async def get_document_result(self, document_id: str)->DocumentResult|None:
        document = await DocumentResult.get(document_id)
        return document

    async def create_document_result(self, document_result:dict) ->DocumentResult:
        document = DocumentResult(**document_result)
        await document.insert()
        return document

    async def update_document_result(self, document_id: str, document_result: dict) ->DocumentResult|None:
        document = await DocumentResult.get(document_id)
        print("doc", document)
        if document:
            await document.update(Set(document_result))
            return document
        return None
    async def delete_document_result(self, document_id: str):
        document = await DocumentResult.get(document_id)
        if document:
            await document.delete()

    async def get_list_of_document_results(self, filters: FilterDocumentResult)-> tuple[list[DocumentResult], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        limit = filter_dump.pop('limit', 10)
        offset = filter_dump.pop('offset', 0)
        if filters.parent_id:
            filter_dump.update(
                In(DocumentResult.parent_id, filters.parent_id)
            )
        if filters.owner_id:
            filter_dump.update(
                In(DocumentResult.owner_id, filters.owner_id)
            )

        query =  DocumentResult.find(filter_dump)
        count = await query.count()

        list_document = await query.skip(offset).limit(limit).to_list()
        return list_document, count
    async def get_all_document_result(self, filters: FilterDocumentResult)->tuple[list[DocumentResult], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        limit = filter_dump.pop('limit', 10)
        offset = filter_dump.pop('offset', 0)
        if filters.parent_id:
            filter_dump.update(
                In(DocumentResult.parent_id, filters.parent_id)
            )
        if filters.owner_id:
            filter_dump.update(
                In(DocumentResult.owner_id, filters.owner_id)
            )

        query =  DocumentResult.find(filter_dump)
        count = await query.count()
        list_document = await query.to_list()
        return list_document, count

    async def get_document_result_by_parent_id(self, parent_id: str, owner_id:str) ->DocumentResult|None:
        document = await DocumentResult.find_one(DocumentResult.parent_id==parent_id, DocumentResult.owner_id==owner_id)
        return document