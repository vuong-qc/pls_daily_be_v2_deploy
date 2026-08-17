from typing import Annotated

from fastapi import APIRouter, status, Depends, Query

from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.testcase.request.create_testcase_model import CreateTestcaseModel
from src.models.testcase.request.filter_testcase_model import FilterTestCaseModel
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem
from src.utils.proxy_util import get_current_user_by_token
from src.routes.document_route import get_document_service, DocumentItemService

router = APIRouter(
    tags=["testcase"],
)


def get_testcase_service(doc_service: DocumentItemService = Depends(get_document_service)):
    return doc_service


@router.post('/create_testcase',
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             )
async def create_document(document: CreateTestcaseModel,
                          service: DocumentItemService = Depends(get_testcase_service),
                          user_data: dict = Depends(get_current_user_by_token)
                          ):
    user_id = user_data.get('sub')
    roles = user_data.get('roles')
    return await service.create_document(document, roles, user_id)


@router.put('/update_testcase/{document_id}',
            response_model=ResponseModel,
            status_code=status.HTTP_202_ACCEPTED,
            )
async def update_document(document_id: str,
                          data: UpdateDocumentItem,
                          service: DocumentItemService = Depends(get_testcase_service),
                          user_data: dict = Depends(get_current_user_by_token)
                          ):
    user_id = user_data.get('sub')
    roles = user_data.get('roles')
    return await service.update_document(document_id, data, user_id, roles)


@router.delete('/delete_testcase/{document_id}',

               status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str,
                          service: DocumentItemService = Depends(get_testcase_service),
                          user_data: dict = Depends(get_current_user_by_token)
                          ):
    user_id = user_data.get('sub')
    return await service.delete_document(document_id, user_id)


@router.get('/list_testcase',

            response_model=ResponsePaginatedModel,
            status_code=status.HTTP_200_OK, )
async def list_documents(
        filters: Annotated[FilterTestCaseModel, Query()],
        service: DocumentItemService = Depends(get_testcase_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data.get('sub')
    return await service.get_list_document(filters, user_id)