from src.enums.user_role_enum import UserRole
from src.enums.version_type_enum import VersionTypeEnum
from src.enums.work_item_type import WorkItemType
from src.exception.version_exception import (
    VersionException,
    VersionMessage,
    VersionStatusCode,
)
from src.models.version.request.create_version_model import CreateVersionModel
from src.models.version.request.filter_version_model import FilterVersionModel
from src.models.version.request.update_version_model import UpdateVersionModel
from src.models.version.response.response_version_model import VersionResponseModel
from src.repositories.department.department_repository import DepartmentRepository
from src.repositories.user.user_repository import UserRepository
from src.repositories.version.version_repository import VersionRepository
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.utils.datetime_util import DateTimeUtil


class VersionService:
    def __init__(
        self,
        repository: VersionRepository,
        work_item_repository: WorkItemRepository,
        department_repository: DepartmentRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.work_item_repository = work_item_repository
        self.department_repository = department_repository
        self.user_repository = user_repository

    async def create_version(
        self, data: CreateVersionModel, user_id: str, roles: list[int]
    ) -> VersionResponseModel:
        await self._authorize_scope(data.type, data.object_id, user_id, roles)
        payload = data.model_dump()
        payload["creator_id"] = user_id
        payload["updator_id"] = user_id
        payload["object_id"] = (
            None if data.type == VersionTypeEnum.PERSONAL else data.object_id
        )
        self._normalize_content(payload)
        version = await self.repository.create_version(payload)
        return VersionResponseModel.model_validate(version)

    async def get_list_versions(
        self, filters: FilterVersionModel, user_id: str, roles: list[int]
    ) -> tuple[list[VersionResponseModel], int]:
        versions, total = await self.repository.get_list_versions(filters, user_id)
        return [VersionResponseModel.model_validate(item) for item in versions], total

    async def get_version(
        self, version_id: str, user_id: str, roles: list[int]
    ) -> VersionResponseModel:
        version = await self._get_authorized_version(version_id, user_id, roles)
        return VersionResponseModel.model_validate(version)

    async def update_version(
        self,
        version_id: str,
        data: UpdateVersionModel,
        user_id: str,
        roles: list[int],
    ) -> VersionResponseModel:
        await self._get_authorized_version(version_id, user_id, roles)
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise VersionException(
                VersionMessage.EMPTY_UPDATE, VersionStatusCode.EMPTY_UPDATE
            )
        payload["updator_id"] = user_id
        self._normalize_content(payload)
        payload["updated_at"] = DateTimeUtil.current_milli_time()
        version = await self.repository.update_version(version_id, payload)
        if not version:
            raise VersionException(VersionMessage.NOT_FOUND, VersionStatusCode.NOT_FOUND)
        return VersionResponseModel.model_validate(version)

    async def delete_version(
        self, version_id: str, user_id: str, roles: list[int]
    ) -> None:
        await self._get_authorized_version(version_id, user_id, roles)
        if not await self.repository.delete_version(version_id):
            raise VersionException(VersionMessage.NOT_FOUND, VersionStatusCode.NOT_FOUND)

    async def _get_authorized_version(self, version_id, user_id, roles):
        version = await self.repository.get_version_by_id(version_id)
        if not version:
            raise VersionException(VersionMessage.NOT_FOUND, VersionStatusCode.NOT_FOUND)
        try:
            version_type = VersionTypeEnum(version.type)
        except ValueError as exc:
            raise VersionException(
                VersionMessage.INVALID_SCOPE, VersionStatusCode.INVALID_SCOPE
            ) from exc
        owner_id = version.creator_id if version_type == VersionTypeEnum.PERSONAL else None
        await self._authorize_scope(
            version_type, version.object_id, user_id, roles, owner_id=owner_id
        )
        return version

    async def _authorize_scope(
        self, version_type, object_id, user_id, roles, owner_id=None
    ) -> None:
        try:
            version_type = VersionTypeEnum(version_type)
        except ValueError as exc:
            raise VersionException(
                VersionMessage.INVALID_SCOPE, VersionStatusCode.INVALID_SCOPE
            ) from exc

        if version_type == VersionTypeEnum.PERSONAL:
            if object_id is not None:
                raise VersionException(
                    VersionMessage.OBJECT_ID_NOT_ALLOWED,
                    VersionStatusCode.OBJECT_ID_NOT_ALLOWED,
                )
            if UserRole.TASKER.value not in roles or (
                owner_id is not None and owner_id != user_id
            ):
                self._raise_forbidden()
            return

        if not object_id:
            raise VersionException(
                VersionMessage.OBJECT_ID_REQUIRED,
                VersionStatusCode.OBJECT_ID_REQUIRED,
            )
        if UserRole.HANDLER.value not in roles:
            self._raise_forbidden()

        if version_type == VersionTypeEnum.PROJECT:
            project = await self.work_item_repository.get_work_item_by_id(object_id)
            if not project or project.type != WorkItemType.PROJECT:
                raise VersionException(
                    VersionMessage.PROJECT_NOT_FOUND,
                    VersionStatusCode.PROJECT_NOT_FOUND,
                )
            if user_id not in (project.handler_id or []):
                self._raise_forbidden()
            return

        department = await self.department_repository.get_department_by_id(object_id)
        if not department:
            raise VersionException(
                VersionMessage.DEPARTMENT_NOT_FOUND,
                VersionStatusCode.DEPARTMENT_NOT_FOUND,
            )
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise VersionException(
                VersionMessage.USER_NOT_FOUND, VersionStatusCode.USER_NOT_FOUND
            )
        if object_id not in (user.department or []):
            self._raise_forbidden()

    @staticmethod
    def _extract_list_scope(filters: FilterVersionModel):
        if not filters.type or len(filters.type) != 1:
            raise VersionException(
                VersionMessage.INVALID_SCOPE, VersionStatusCode.INVALID_SCOPE
            )
        version_type = filters.type[0]
        if version_type == VersionTypeEnum.PERSONAL:
            if filters.object_id:
                raise VersionException(
                    VersionMessage.OBJECT_ID_NOT_ALLOWED,
                    VersionStatusCode.OBJECT_ID_NOT_ALLOWED,
                )
            return version_type, None
        if not filters.object_id or len(filters.object_id) != 1:
            raise VersionException(
                VersionMessage.OBJECT_ID_REQUIRED,
                VersionStatusCode.OBJECT_ID_REQUIRED,
            )
        return version_type, filters.object_id[0]

    @staticmethod
    def _normalize_content(payload: dict) -> None:
        if "title" in payload:
            title = payload["title"].strip()
            if not title:
                raise VersionException(
                    VersionMessage.TITLE_REQUIRED, VersionStatusCode.TITLE_REQUIRED
                )
            payload["title"] = title
        if isinstance(payload.get("description"), str):
            payload["description"] = payload["description"].strip() or None
        if payload.get("files") is not None:
            payload["files"] = list(dict.fromkeys(payload["files"]))

    @staticmethod
    def _raise_forbidden() -> None:
        raise VersionException(VersionMessage.FORBIDDEN, VersionStatusCode.FORBIDDEN)
