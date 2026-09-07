from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.version.request.create_version_model import CreateVersionModel
from src.models.version.request.filter_version_model import FilterVersionModel
from src.models.version.request.update_version_model import UpdateVersionModel
from src.repositories.department.beanie_department_repository import (
    BeanieDepartmentRepository,
)
from src.repositories.user.beanie_user_repository import BeanieUserRepository
from src.repositories.version.beanie_version_repository import BeanieVersionRepository
from src.repositories.work_item.beanie_work_item_repository import (
    BeanieWorkItemRepository,
)
from src.services.version_service import VersionService
from src.utils.proxy_util import get_current_user_by_token


router = APIRouter(tags=["version"])


def get_version_service() -> VersionService:
    return VersionService(
        BeanieVersionRepository(),
        BeanieWorkItemRepository(),
        BeanieDepartmentRepository(),
        BeanieUserRepository(),
    )


@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_version(
    data: CreateVersionModel,
    service: VersionService = Depends(get_version_service),
    user_data: dict = Depends(get_current_user_by_token),
):
    return ResponseModel(
        data=await service.create_version(data, user_data["sub"], user_data["roles"])
    )


@router.get("", response_model=ResponsePaginatedModel)
async def get_list_versions(
    query: Annotated[FilterVersionModel, Query()],
    service: VersionService = Depends(get_version_service),
    user_data: dict = Depends(get_current_user_by_token),
):
    versions, total = await service.get_list_versions(
        query, user_data["sub"], user_data["roles"]
    )
    return ResponsePaginatedModel(
        data=versions, total=total, offset=query.offset
    )


@router.get("/{version_id}", response_model=ResponseModel)
async def get_version(
    version_id: str,
    service: VersionService = Depends(get_version_service),
    user_data: dict = Depends(get_current_user_by_token),
):
    return ResponseModel(
        data=await service.get_version(
            version_id, user_data["sub"], user_data["roles"]
        )
    )


@router.patch("/{version_id}", response_model=ResponseModel)
async def update_version(
    version_id: str,
    data: UpdateVersionModel,
    service: VersionService = Depends(get_version_service),
    user_data: dict = Depends(get_current_user_by_token),
):
    return ResponseModel(
        data=await service.update_version(
            version_id, data, user_data["sub"], user_data["roles"]
        )
    )


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(
    version_id: str,
    service: VersionService = Depends(get_version_service),
    user_data: dict = Depends(get_current_user_by_token),
):
    await service.delete_version(version_id, user_data["sub"], user_data["roles"])
