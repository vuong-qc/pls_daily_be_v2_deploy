from typing import Optional

from fastapi import APIRouter, Depends, status, Query

from src.models.response_model import ResponseModel
from src.models.section.request.section_model import CreateSectionItemModel, CreateSectionModel, UpdateSectionModel
from src.repositories.section.beanie_section_repository import BeanieSectionRepository
from src.repositories.template.beanie_template_repository import BeanieTemplateRepository
from src.services.section_service import SectionService
from src.utils.proxy_util import get_current_user_by_token

router = APIRouter(tags=["section"])


def get_section_service():
    return SectionService(BeanieSectionRepository(), BeanieTemplateRepository())


@router.post("/create-sections", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_section(data: CreateSectionModel,
                         service: SectionService = Depends(get_section_service),
                         user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.create_section(data.template_id, data, user_data["sub"]))


@router.post("/create-sections-items", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_section_item(data: CreateSectionItemModel,
                              service: SectionService = Depends(get_section_service),
                              user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.create_section_item(data.section_id, data, user_data["sub"]))


@router.patch("/update-section/{section_id}", response_model=ResponseModel)
async def update_section(section_id: str, data: UpdateSectionModel,
                         service: SectionService = Depends(get_section_service),
                         user_data: dict = Depends(get_current_user_by_token)):
    return ResponseModel(data=await service.update_section(section_id, data, user_data["sub"]))


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(section_id: str, service: SectionService = Depends(get_section_service),
                         user_data: dict = Depends(get_current_user_by_token)):
    await service.delete_section(section_id, user_data["sub"])


@router.get("/get-list-section", response_model=ResponseModel)
async def get_sections(
        list_type: Optional[list[str]] = Query(None),
        parent_ids: Optional[list[str]] = Query(None),
        categories: Optional[list[str]] = Query(None),
        value_types: Optional[list[str]] = Query(None),
        search: Optional[str] = Query(None),
        service: SectionService = Depends(get_section_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return ResponseModel(
        data=await service.get_sections(
            list_type=list_type,
            parent_ids=parent_ids,
            categories=categories,
            value_types=value_types,
            search=search,
        )
    )
