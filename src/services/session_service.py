from src.repositories.session.session_repository import SessionRepository
from src.models.session.request.filter_session_model import FilterSessionModel
from src.models.session.request.update_session_model import UpdateSessionModel, CheckoutModel, UpdateSubTaskModel
from src.models.session.request.create_session_model import CreateSessionModel
from src.models.session.response.session_response_model import SessionResponse
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.exception.session_exception import SessionException, SessionMessage, SessionStatusCode
from src.exception.task_exception import TaskException, TaskStatusCode, TaskMessage
from src.enums.work_item_type import WorkItemType
from src.enums.task_status_enum import TaskStatusEnum
from src.models.task.request.update_task_model import UpdateTaskModel
import asyncio
from datetime import datetime
from src.enums.session_status_enum import SessionStatusEnum

class SessionService:
    def __init__(self, session_repository: SessionRepository, work_item_repository: WorkItemRepository):
        self.session_repository = session_repository
        self.work_item_repository = work_item_repository

    async def create_session(self, session_data: CreateSessionModel) -> ResponseModel:
        new_session = await self.session_repository.create_session(session_data.model_dump())
        response = SessionResponse.model_validate(new_session)
        return ResponseModel(data=response)

    async def update_session(self, session_id:str, session_data: UpdateSessionModel, user_id:str) -> ResponseModel:
        updated_session = await self.session_repository.update_session(session_id, session_data.model_dump(exclude_unset=True))
        if not updated_session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)
        if user_id != updated_session.user_id:
            raise SessionException(SessionMessage.NOT_OWNER, SessionStatusCode.NOT_OWNER)
        response = SessionResponse.model_validate(updated_session)
        return ResponseModel(data=response)
    async def delete_session(self, session_id:str):
        await self.session_repository.delete_session(session_id)

    async def get_session(self, session_id:str):
        session = await self.session_repository.get_session_by_id(session_id)
        if not session:
            raise
        response = SessionResponse.model_validate(session)
        return ResponseModel(data=response)

    async def get_list_sessions(self, filters: FilterSessionModel)-> ResponsePaginatedModel:
        list_sessions, total = await self.session_repository.get_list_session(filters)

        list_sessions_response = []
        for session in list_sessions:
            response = SessionResponse.model_validate(session)
            list_sessions_response.append(response)
        return ResponsePaginatedModel(data=list_sessions_response, total=total, offset= filters.offset)


    async def checkout(self, user_id: str, session_id:str, session_data: CheckoutModel):
        session = await self.session_repository.get_session_by_id(session_id)
        if not session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)

        # update work item: task, subtask,
        # add session_id in to subtask
        if user_id != session.user_id:
            raise SessionException(SessionMessage.NOT_OWNER, SessionStatusCode.NOT_OWNER)

        # task or subtask
        await asyncio.gather(*[
            self._handle_update_task(item, session_id)
            for item in session_data.list_subtasks
        ])
        # update session
        update_session_data = UpdateSessionModel(status=SessionStatusEnum.DONE, end_time=session_data.end_time)
        if not update_session_data.end_time:
            update_session_data.end_time = datetime.now()
        data_dump = update_session_data.model_dump(exclude_unset=True)
        updated_session = await self.session_repository.update_session(session_id, data_dump)
        if not updated_session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)
        response = SessionResponse.model_validate(updated_session)
        return ResponseModel(data=response)

    async def _handle_update_task(self, item: UpdateSubTaskModel, session_id:str):
        work_item = await self.work_item_repository.get_work_item_by_id(item.id)
        if not work_item:
            raise TaskException(TaskMessage.SUBTASK_NOT_FOUND, TaskStatusCode.SUBTASK_NOT_FOUND)

        if work_item.type not in [WorkItemType.TASK.value, WorkItemType.SUBTASK.value]:
            raise SessionException(SessionMessage.TASK_SUBTASK_TYPE_NOT_MATCH,
                                   SessionStatusCode.TASK_SUBTASK_TYPE_NOT_MATCH)

        if work_item.type == WorkItemType.SUBTASK.value and item.status == TaskStatusEnum.DONE.value:
            update_data = UpdateTaskModel(status=item.status, session_id=session_id)
            await self.work_item_repository.update_work_item(item.id, update_data.model_dump(exclude_unset=True))

        else:
            update_data = UpdateTaskModel(status=item.status)
            await self.work_item_repository.update_work_item(item.id, update_data.model_dump(exclude_unset=True))
