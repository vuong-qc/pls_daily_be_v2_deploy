from dataclasses import dataclass
from typing import Optional

from src.enums.work_item_type import WorkItemType
from src.enums.task_status_enum import TaskStatusEnum
from src.enums.sprint_status_enum import SprintStatusEnum
from src.exception.duplicate_work_item_exception import (
    DuplicateWorkItemException,
    DuplicateWorkItemMessage as Msg,
)
from src.models.response_model import ResponseModel
from src.models.work_item.request.duplicate_work_item_model import DuplicateWorkItemRequest
from src.models.work_item.response.work_item_response_model import WorkItemResponse
from src.models.work_item.work_item_document import WorkItemDocument
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.utils.datetime_util import DateTimeUtil

SYSTEM_FIELDS = {
    "id", "_id", "revision_id", "is_deleted", "deleted_at",
    "created_at", "updated_at", "parent", "parent_model",
    "owner", "assignee", "handler", "assigned_id", "handler_id",
    "status", "session_id",
}

DESCENDANT_ALLOWED_TYPES: dict[str, list[str]] = {
    WorkItemType.SPRINT: [WorkItemType.STORY, WorkItemType.TASK],
    WorkItemType.STORY: [WorkItemType.TASK],
}


@dataclass(frozen=True)
class DestinationContext:
    project_id: str
    parent_id: str
    project: WorkItemDocument
    sprint: Optional[WorkItemDocument] = None
    story: Optional[WorkItemDocument] = None


@dataclass(frozen=True)
class SourceContext:
    root: WorkItemDocument
    project_id: str
    sprint_id: str


class DuplicateWorkItemService:
    def __init__(self, work_item_repository: WorkItemRepository):
        self.work_item_repository = work_item_repository

    # ---------------- Public entrypoint ----------------

    async def duplicate(
        self, source_id: str, req: DuplicateWorkItemRequest, actor_id: str
    ) -> ResponseModel:
        source_ctx = await self._resolve_source_context(source_id)
        destination = await self._resolve_destination(source_ctx.root, req)
        self._require_destination_project_handler(destination.project, actor_id)

        levels = await self._load_and_validate_tree(source_ctx.root)
        now = DateTimeUtil.current_milli_time()

        id_map: dict[str, str] = {}
        new_root: Optional[WorkItemDocument] = None

        async with self.work_item_repository.transaction() as session:
            for level in levels:
                payloads = []
                for node in level:
                    is_root = str(node.id) == str(source_ctx.root.id)

                    parent_id = (
                        destination.parent_id
                        if str(node.id) == str(source_ctx.root.id)
                        else id_map[str(node.parent)]
                    )
                    payload = self._build_duplicate_payload(node, parent_id, actor_id, id_map, now)
                    if is_root:
                        payload["title"] = f"Copy - {node.title}"

                    payloads.append(
                        payload
                    )

                inserted = await self.work_item_repository.create_many_work_items(
                    payloads, session=session
                )
                print("inserted", inserted)
                for old, new in zip(level, inserted):
                    id_map[str(old.id)] = str(new)
                    if str(old.id) == str(source_ctx.root.id):
                        new_root = await self.work_item_repository.get_work_item_by_id(str(new), session=session)

        return ResponseModel(data=WorkItemResponse.model_validate(new_root))

    # ---------------- Source resolver ----------------

    async def _require_type(self, item_id: str, expected_type: str) -> WorkItemDocument:
        item = await self.work_item_repository.get_work_item_by_id(item_id)
        if not item:
            raise DuplicateWorkItemException(Msg.DESTINATION_NOT_FOUND, 404)
        if item.type != expected_type:
            raise DuplicateWorkItemException(Msg.DESTINATION_TYPE_MISMATCH, 400)
        return item

    async def _resolve_source_context(self, source_id: str) -> SourceContext:
        source = await self.work_item_repository.get_work_item_by_id(source_id)
        if not source:
            raise DuplicateWorkItemException(Msg.SOURCE_NOT_FOUND, 404)
        if source.type not in {WorkItemType.TASK, WorkItemType.STORY, WorkItemType.SPRINT}:
            raise DuplicateWorkItemException(Msg.SOURCE_TYPE_NOT_SUPPORTED, 400)

        if source.type == WorkItemType.SPRINT:
            project = await self._require_type(source.parent, WorkItemType.PROJECT)
            return SourceContext(source, str(project.id), str(source.id))

        if source.type == WorkItemType.STORY:
            sprint = await self._require_type(source.parent, WorkItemType.SPRINT)
            project = await self._require_type(sprint.parent, WorkItemType.PROJECT)
            return SourceContext(source, str(project.id), str(sprint.id))

        # TASK
        parent = await self.work_item_repository.get_work_item_by_id(source.parent)
        if not parent:
            raise DuplicateWorkItemException(Msg.SOURCE_SCOPE_NOT_SUPPORTED, 400)

        if parent.type == WorkItemType.STORY:
            sprint = await self._require_type(parent.parent, WorkItemType.SPRINT)
        elif parent.type == WorkItemType.SPRINT:
            sprint = parent
        else:
            # BACKLOG cá nhân hoặc backlog project — chưa hỗ trợ làm nguồn.
            raise DuplicateWorkItemException(Msg.SOURCE_SCOPE_NOT_SUPPORTED, 400)

        project = await self._require_type(sprint.parent, WorkItemType.PROJECT)
        return SourceContext(source, str(project.id), str(sprint.id))

    # ---------------- Destination resolver ----------------

    async def _resolve_destination(
        self, source: WorkItemDocument, req: DuplicateWorkItemRequest
    ) -> DestinationContext:
        project = await self._require_type(req.project_id, WorkItemType.PROJECT)

        if source.type == WorkItemType.TASK:
            if not req.sprint_id:
                raise DuplicateWorkItemException(Msg.DESTINATION_SPRINT_REQUIRED, 400)
            sprint = await self._require_type(req.sprint_id, WorkItemType.SPRINT)
            if str(sprint.parent) != str(project.id):
                raise DuplicateWorkItemException(Msg.DESTINATION_TREE_MISMATCH, 400)

            if req.story_id:
                story = await self._require_type(req.story_id, WorkItemType.STORY)
                if str(story.parent) != str(sprint.id):
                    raise DuplicateWorkItemException(Msg.DESTINATION_TREE_MISMATCH, 400)
                return DestinationContext(str(project.id), str(story.id), project, sprint, story)

            return DestinationContext(str(project.id), str(sprint.id), project, sprint)

        if source.type == WorkItemType.STORY:
            if not req.sprint_id:
                raise DuplicateWorkItemException(Msg.DESTINATION_SPRINT_REQUIRED, 400)
            if req.story_id:
                raise DuplicateWorkItemException(Msg.DESTINATION_FIELD_NOT_ALLOWED, 400)
            sprint = await self._require_type(req.sprint_id, WorkItemType.SPRINT)
            if str(sprint.parent) != str(project.id):
                raise DuplicateWorkItemException(Msg.DESTINATION_TREE_MISMATCH, 400)
            return DestinationContext(str(project.id), str(sprint.id), project, sprint)

        # SPRINT
        if req.sprint_id or req.story_id:
            raise DuplicateWorkItemException(Msg.DESTINATION_FIELD_NOT_ALLOWED, 400)
        return DestinationContext(str(project.id), str(project.id), project)

    # ---------------- Permission ----------------

    def _require_destination_project_handler(self, project: WorkItemDocument, actor_id: str):
        handlers = set(project.handler_id or [])
        if actor_id not in handlers:
            raise DuplicateWorkItemException(Msg.NOT_HANDLER_DESTINATION_PROJECT, 403)

    # ---------------- Load & validate source tree ----------------

    async def _load_and_validate_tree(
        self, root: WorkItemDocument
    ) -> list[list[WorkItemDocument]]:
        levels: list[list[WorkItemDocument]] = [[root]]

        current_parents = [str(root.id)]
        allowed_types = DESCENDANT_ALLOWED_TYPES.get(root.type)

        while allowed_types:
            children = await self.work_item_repository.get_active_children(
                current_parents, allowed_types
            )
            if not children:
                break

            # Validate: mỗi children phải thuộc allowed_types (get_active_children đã filter,
            # nhưng nếu muốn reject cây có child ngoài matrix thì kiểm tra thêm ở đây bằng
            # cách so sánh tổng children thực tế trong DB với children filter được, tuỳ mức
            # nghiêm ngặt team muốn áp dụng).

            levels.append(children)
            current_parents = [str(c.id) for c in children]

            # Cấp tiếp theo chỉ tồn tại nếu node vừa lấy là STORY (SPRINT->STORY->TASK).
            # TASK không có allowed_types tiếp theo -> dừng lại, không đụng SUBTASK.
            next_types_set = set()
            for c in children:
                if c.type in DESCENDANT_ALLOWED_TYPES:
                    next_types_set.update(DESCENDANT_ALLOWED_TYPES[c.type])
            allowed_types = list(next_types_set) if next_types_set else None
        print("levels", levels)
        return levels

    # ---------------- Payload builder ----------------

    def _build_duplicate_payload(
        self,
        node: WorkItemDocument,
        parent_id: str,
        actor_id: str,
        id_map: dict[str, str],
        now: int,
    ) -> dict:
        data = node.model_dump(exclude=SYSTEM_FIELDS)
        data["parent"] = parent_id
        data["owner_id"] = actor_id
        data["assigned_id"] = None
        data["handler_id"] = None
        data["created_at"] = now
        data["updated_at"] = now
        data["session_id"] = None

        if node.type == WorkItemType.TASK:
            data["status"] = TaskStatusEnum.NEW
        elif node.type == WorkItemType.SPRINT:
            data["status"] = SprintStatusEnum.NEW
        elif node.type == WorkItemType.STORY:
            data["status"] = None

        data = self._remap_denormalized_refs(data, id_map, node)
        return data

    def _remap_denormalized_refs(
        self, data: dict, id_map: dict[str, str], node: WorkItemDocument
    ) -> dict:
        # Không remap chuỗi tự do (link/note/comment). Chỉ remap reference có ý nghĩa cấu trúc.
        if data.get("task") and data["task"] in id_map:
            data["task"] = id_map[data["task"]]
        if data.get("sprint") and data["sprint"] in id_map:
            data["sprint"] = id_map[data["sprint"]]
        # project của node mới luôn theo destination project_id — set ở service._build...
        # nếu field `project` được dùng để lưu id project, gán ở đây tuỳ schema thật.
        return data