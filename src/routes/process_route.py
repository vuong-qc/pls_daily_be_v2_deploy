from typing import Annotated

from fastapi import APIRouter, Depends, status, Query, Header, HTTPException
from src.routes.report_route import get_section_result_service
from src.services.section_result_service import SectionResultService
from src.utils.proxy_util import get_current_user_by_token
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.section_result.request.section_result_model import FilterResultModel, FilterResultProcessModel


router = APIRouter(tags=["process"])

@router.get("/get-process-date-range", response_model=ResponseModel)
async def get_list_process_range(
        query: Annotated[FilterResultModel, Query()],
        service: SectionResultService = Depends(get_section_result_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    data = await service.get_process_result_by_range(query)
    return ResponseModel(data=data)

@router.get("/get-process", response_model=ResponseModel)
async def get_list_process(
        query: Annotated[FilterResultProcessModel, Query()],
        service: SectionResultService = Depends(get_section_result_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    data = await service.get_process_results(query.template_id, query.user_id, query.date)
    return ResponseModel(data=data)