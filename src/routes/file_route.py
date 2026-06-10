from datetime import time

from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, Query, Request, BackgroundTasks
from src.repositories.file.beanie_file_repository import BeanieFileRepository
from src.services.file_service import FileService
from src.models.file.update_file_model import UpdateFileName
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
from src.utils.jwt_bearer_util import JWTBearerUtil
from src.utils.role_checker_util import RoleCheckerUtil
from src.database import db
from src.utils.proxy_util import get_current_user_by_token


def get_file_service():
    repo = BeanieFileRepository(db)
    return FileService(repo)


# use this with window
# poppler_path = r"C:\tool\Release-25.12.0-0\poppler-25.12.0\Library\bin"

router = APIRouter(
    tags=["upload"]
)


@router.post(
    "/upload-file",
    summary="Upload File",
    description="Uploads a file, stores it, and generates a thumbnail when the file type is supported.",
)
async def upload_file(file: UploadFile,
                      background_tasks: BackgroundTasks,
                      service: FileService = Depends(get_file_service),
                      user_data: dict = Depends(get_current_user_by_token),
                      ):
    return await service.upload_file(file, background_tasks)


@router.post(
    "/create-thumbnail",
    summary="Create Thumbnail",
    description="Create Thumbnail",
)
async def create_thumbnail(file: UploadFile, file_id: str,
                           service: FileService = Depends(get_file_service),
                           user_data: dict = Depends(get_current_user_by_token),
                           ):
    return await service.create_thumbnail(file, f"thumbnail_{file_id}")


@router.put(
    "/rename-file/{id}",
    summary="Rename File",
    description="Renames a stored file by ID. Thumbnail records cannot be renamed.",
)
async def rename_file(id: str, data: UpdateFileName,
                      service: FileService = Depends(get_file_service),
                      user_data: dict = Depends(get_current_user_by_token),
                      ):
    return await service.rename_file(id, data)


@router.get(
    "/get-file/{id}",
    summary="Get File",
    description="Streams the original file content for the specified file ID.",
)
async def get_file_by_id(id: str, request: Request, service: FileService = Depends(get_file_service),
                         download: bool = Query(False),
                         # user_data: dict = Depends(get_current_user_by_token),
                         ):
    return await service.get_file(id, request.headers.get("range"), download)


@router.head(
    "/get-file/{id}",
    summary="Get File Metadata",
    description="Returns headers for the specified file ID without streaming the file body.",
)
async def get_file_head_by_id(id: str, service: FileService = Depends(get_file_service)):
    return await service.get_file_metadata(id)


@router.get(
    "/get-thumbnail/{id}",
    summary="Get Thumbnail",
    description="Streams the thumbnail content for the specified thumbnail file ID.",
)
async def get_thumbnail_by_id(id: str, service: FileService = Depends(get_file_service),
                              # user_data: dict = Depends(get_current_user_by_token),
                              ):
    return await service.get_thumbnail(id)


@router.delete(
    "/delete-file/{id}",
    summary="Delete File",
    description="Marks a stored file as deleted by ID.",
)
async def delete_file_by_id(id: str, service: FileService = Depends(get_file_service),
                            user_data: dict = Depends(get_current_user_by_token)
                            ):
    return await service.delete_file(id)


@router.post("/upload-multi-files")
async def upload_multi_files(files: list[UploadFile], background_tasks: BackgroundTasks,
                             service: FileService = Depends(get_file_service)):
    results = await service.upload_multiple_files(files, background_tasks)
    return {"data": results}


@router.get("/get-info-by-id")
async def get_info_by_id(file_id: str,
                              service: FileService = Depends(get_file_service),
                              # user_data: dict = Depends(get_current_user_by_token)
                              ):
    return await service.get_info_by_id(file_id)

@router.get("/get-info-files-by-ids")
async def get_info_files_by_ids(file_ids: list[str] = Query(None),
        service: FileService = Depends(get_file_service),
        user: dict = Depends(get_current_user_by_token),
):
    return await service.get_info_files_by_ids(file_ids)
