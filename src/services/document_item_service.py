from typing import Optional

from src.exception.project_exception import ProjectException, ProjectMessage, ProjectStatusCode
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.document_item.beanie_document_item_repository import DocumentItemRepository
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem
from src.models.document_item.request.create_document_item_model import CreateDocumentItem
from src.models.document_item.response.document_item_response_model import DocumentResponse
from src.exception.document_exception import DocumentException, DocumentMessage, DocumentStatusCode
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.document_result.response.document_result_response import DocumentResultResponse
from src.repositories.document_result.document_result_repository import DocumentResultRepository
# from src.exception.sprint_exception import SprintException, SprintMessage, SprintStatusCode
from src.enums.work_item_type import DocumentParentType, WorkItemType
from src.models.document_result.request.create_document_result_model import CreateDocumentResult
from src.models.document_result.request.update_document_result_model import UpdateDocumentResult
# from src.models.document_result.request.filter_document_result_model import FilterDocumentResult
from src.enums.user_role_enum import UserRole


from src.enums.document_type_enum import DocumentTypeEnum

class DocumentItemService:
    def __init__(self, repository: DocumentItemRepository, work_item_repository: WorkItemRepository, document_result_repository: DocumentResultRepository):
        self.repository = repository
        self.work_item_repository = work_item_repository
        self.document_result_repository = document_result_repository

    async def create_document(self, data: CreateDocumentItem, roles: Optional[list]=None, user_id: Optional[str] = None) -> ResponseModel:
        if data.type == DocumentTypeEnum.TODO and data.ftf:
            # check first thing first, count todo
            # if count = 5 raise error
            filter_todo = FilterDocumentItem(type=[DocumentTypeEnum.TODO], offset=0, limit=1, object_id=[data.object_id], ftf=True, is_checked=False)
            list_doc, total = await self.repository.get_list_document_items(filter_todo)
            if total>= 5:
                raise DocumentException(DocumentMessage.CANT_ASSIGN_FTF, DocumentStatusCode.CANT_ASSIGN_FTF)

        #write func check for group
        # check role for type
        data.created_by = user_id
        # if data.parent_type and data.object_id:
        #     await self._check_role_with_doc_type(data.type, roles, data.created_by,data.object_id, data.parent_type)
        document = await self.repository.create_document(data.model_dump())
        response = DocumentResponse.model_validate(document)
        # auto create doc result
        create_result_data = CreateDocumentResult(parent_id = str(response.id), owner_id=user_id)
        result = await self.document_result_repository.create_document_result(create_result_data.model_dump())
        response.result = DocumentResultResponse.model_validate(result)
        return ResponseModel(data=response)

    async def update_document(self, document_id:str, data: UpdateDocumentItem, user_id:str, roles: Optional[list[int]] = None,) -> ResponseModel:
        old_document = await self.repository.get_document_item(document_id)
        if not old_document:
            raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        if old_document.type == DocumentTypeEnum.TODO and data.ftf:
            # check first thing first, count todo
            # if count = 5 raise error
            filter_todo = FilterDocumentItem(type=[DocumentTypeEnum.TODO], offset=0, limit=1, object_id=[old_document.object_id], ftf=True, is_checked=False)
            list_doc, total = await self.repository.get_list_document_items(filter_todo)
            if total>= 5:
                raise DocumentException(DocumentMessage.CANT_ASSIGN_FTF, DocumentStatusCode.CANT_ASSIGN_FTF)

        document = await self.repository.update_document(document_id, data)
        if not document:
             raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        # if document.parent_type:
        #     await self._check_role_with_doc_type(document.type, roles, user_id,document.object_id, document.parent_type)

        response = DocumentResponse.model_validate(document)
        return ResponseModel(data=response)

    async def update_document_result(self, user_id:str, document_result_id:str, data: UpdateDocumentResult) -> ResponseModel:
        doc_result = await self.document_result_repository.get_document_result(document_result_id)
        if not doc_result:
            raise DocumentException(DocumentMessage.DOCUMENT_RESULT_NOT_FOUND, DocumentStatusCode.DOCUMENT_RESULT_NOT_FOUND)
        # if doc_result.owner_id != user_id:
        #     raise DocumentException(DocumentMessage.NOT_CREATOR, DocumentStatusCode.NOT_CREATOR)
        print("doc result", doc_result)
        updated_document = await self.document_result_repository.update_document_result(document_result_id, data.model_dump(exclude_unset=True))
        if not updated_document:
            raise DocumentException(DocumentMessage.DOCUMENT_RESULT_NOT_FOUND, DocumentStatusCode.DOCUMENT_RESULT_NOT_FOUND)
        return ResponseModel(data=DocumentResultResponse.model_validate(updated_document))

    async def delete_document(self, document_id:str, user_id: str):
        document = await self.repository.get_document_item(document_id)
        if not document:
            raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        if document.created_by and document.created_by != user_id:
            raise DocumentException(DocumentMessage.NOT_CREATOR, DocumentStatusCode.NOT_CREATOR)
        await self.repository.delete_document(document_id)
        return ResponseModel()

    async def get_document(self, document_id:str):
        document = await self.repository.get_document_item(document_id)
        if not document:
            raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        response = DocumentResponse.model_validate(document)
        return ResponseModel(data=response)

    async def get_list_document(self, filters: FilterDocumentItem, user_id: str) -> ResponsePaginatedModel:
        list_document, total = await self.repository.get_list_document_items(filters)
        list_res = []
        for document in list_document:
            response = DocumentResponse.model_validate(document)
            # get result of doc
            result = await self.document_result_repository.get_document_result_by_parent_id(str(response.id),user_id)
            if not result:
                create_result_data = CreateDocumentResult(parent_id=str(response.id))
                create_result_data.owner_id = user_id
                result = await self.document_result_repository.create_document_result(create_result_data.model_dump())
            response.result = DocumentResultResponse.model_validate(result)
            list_res.append(response)
        return ResponsePaginatedModel(data=list_res, total=total, offset=filters.offset)

    async def _check_role_with_doc_type(self,doc_type:str, roles: list[int], user_id:str, object_id: Optional[str] = None, parent_type: Optional[str] = None):
        if object_id and user_id and parent_type:
            # check work_item exist and match type
            work_item = await self.work_item_repository.get_work_item_by_id(object_id)
            if not work_item:
                raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
            if work_item.type != parent_type:
                raise DocumentException(DocumentMessage.PARENT_TYPE_NOT_MATCH, DocumentStatusCode.PARENT_TYPE_NOT_MATCH)
            if doc_type == DocumentTypeEnum.QA:
                if UserRole.TASKER.value in roles:
                    if work_item.type != WorkItemType.SPRINT or parent_type != WorkItemType.SPRINT:
                        raise DocumentException(DocumentMessage.TASKER_NOT_MATCH_SPRINT, DocumentStatusCode.TASKER_NOT_MATCH_SPRINT)
                    # parent type is sprint
                    else:
                        if user_id not in work_item.assigned_id:
                            raise DocumentException(DocumentMessage.TASKER_NOT_MATCH_SPRINT, DocumentStatusCode.TASKER_NOT_MATCH_SPRINT)

                elif UserRole.HANDLER.value in roles:
                    if work_item.type == WorkItemType.SPRINT:
                        project = await self.work_item_repository.get_work_item_by_id(work_item.parent)
                        if not project:
                            raise ProjectException(ProjectMessage.NOT_FOUND, ProjectStatusCode.NOT_FOUND)
                        if user_id not in project.handler_id:
                            raise ProjectException(ProjectMessage.NOT_HANDLER_PROJECT, ProjectStatusCode.NOT_HANDLER_PROJECT)
                    elif work_item.type == WorkItemType.PROJECT:
                        if user_id not in work_item.handler_id:
                            raise ProjectException(ProjectMessage.NOT_HANDLER_PROJECT, ProjectStatusCode.NOT_HANDLER_PROJECT)
        else:
            raise DocumentException(DocumentMessage.NOT_ENOUGH_DATA, DocumentStatusCode.NOT_ENOUGH_DATA)

    async def statistic_todo(self, query: FilterDocumentItem):
        total_todo = await self.repository.count_items_by_time_buckets(query)
        query.is_checked = True
        todo_done_todo = await self.repository.count_completed_items_by_time_buckets(query)
        return ResponseModel(data={
            "total_todo": total_todo,
            "todo_done_todo": todo_done_todo
        })
    #
    # async def count_checklist_doc_qa(self, query: FilterDocumentItem):
    #     DocumentTypeEnum.CHECKLIST # total and resolve
    #     DocumentTypeEnum.QA # total and resolve
    #     WorkItemType.BUG # total and resolve
    #     DocumentTypeEnum.DOCUMENT # total