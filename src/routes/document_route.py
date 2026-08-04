from typing import Annotated, Optional

from fastapi import APIRouter, status, Depends, Query

from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.document_item.beanie_document_item_repository import BeanieDocumentItemRepository
from src.models.document_item.request.create_document_item_model import CreateDocumentItem
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem
from src.services.document_item_service import DocumentItemService
from src.utils.proxy_util import get_current_user_by_token
from src.models.document_result.request.update_document_result_model import UpdateDocumentResult
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.repositories.document_result.beanie_document_result_repository import BeanieDocumentResultRepository

router = APIRouter(
    tags=["document"],
)

def get_document_service():
    repository = BeanieDocumentItemRepository()
    work_item_repository = BeanieWorkItemRepository()
    document_result_repository = BeanieDocumentResultRepository()
    return DocumentItemService(repository, work_item_repository, document_result_repository)

@router.post('/create_document',
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
)
async def create_document(document: CreateDocumentItem,
                          service: DocumentItemService = Depends(get_document_service),
                          user_data: dict = Depends(get_current_user_by_token)
                          ):
    user_id = user_data.get('sub')
    roles = user_data.get('roles')
    return await service.create_document(document, roles, user_id)

@router.put('/update_document/{document_id}',
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            )
async def update_document(document_id: str,
                          data: UpdateDocumentItem,
                          service: DocumentItemService = Depends(get_document_service),
                          user_data: dict = Depends(get_current_user_by_token)
                          ):
    user_id = user_data.get('sub')
    roles = user_data.get('roles')
    return await service.update_document(document_id, data, user_id, roles)

@router.put('/update-document-result/{document_id}',
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            )
async def update_document_result(document_id: str,
                                 data: UpdateDocumentResult,
                                 service: DocumentItemService = Depends(get_document_service),
                                 user_data: dict = Depends(get_current_user_by_token)
                                 ):
    user_id = user_data.get('sub')
    return await service.update_document_result(user_id, document_id, data)

@router.delete('/delete_document/{document_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str,
                          service: DocumentItemService = Depends(get_document_service),
                          user_data: dict = Depends(get_current_user_by_token)
                          ):
    user_id = user_data.get('sub')
    return await service.delete_document(document_id, user_id)

@router.get('/list_documents',

            response_model=ResponsePaginatedModel,
            status_code=status.HTTP_200_OK,)
async def list_documents(
        filters: Annotated[FilterDocumentItem, Query()],
        service: DocumentItemService = Depends(get_document_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data.get('sub')
    return await service.get_list_document(filters, user_id)

@router.get('/statistic-todo',
            response_model=ResponseModel,
            status_code=status.HTTP_200_OK
            )
async def statistic_todo(
        query: Annotated[FilterDocumentItem, Query()],
        service: DocumentItemService = Depends(get_document_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await service.statistic_todo(query)