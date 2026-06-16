from src.models.task.response.task_response_model import TaskResponse
from src.models.work_item.request import filter_work_item
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.repositories.session.session_repository import SessionRepository
from src.models.session.request.filter_session_model import FilterSessionModel, FilterCheckInSessionModel
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
from datetime import datetime
from src.utils.datetime_util import DateTimeUtil
from src.repositories.user.user_repository import UserRepository
from src.repositories.chatbot_token.chatbot_token_repository import ChatbotTokenRepository
from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel
from src.utils.google_chat_webhook_util import GgChatWebhookUtil
from src.utils.form_text_gg_chat_api import FormatContentGgChatAPI
import asyncio
from src.enums.session_status_enum import SessionStatusEnum
import logging
logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self, session_repository: SessionRepository, work_item_repository: WorkItemRepository,
                 chatbot_token_repository: ChatbotTokenRepository, user_repository: UserRepository,):
        self.session_repository = session_repository
        self.work_item_repository = work_item_repository
        self.chatbot_token_repository = chatbot_token_repository
        self.user_repository = user_repository

    async def create_session(self, session_data: CreateSessionModel) -> ResponseModel:
        new_session = await self.session_repository.create_session(session_data.model_dump())
        logger.info('checkin success with data: %s',new_session)
        created_session = await self.session_repository.get_session_by_id(str(new_session.id))
        response = SessionResponse.model_validate(created_session)
        # inject call webhook
        # get token
        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=1)
        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        if total > 0:
            list_task = []
            await asyncio.gather(*[
                self.get_work_item_by_id(work_id, list_task)
                for work_id in session_data.list_task
            ])
            content = FormatContentGgChatAPI.format_content_checkin(response.user.name, list_task,session_data.notes)
            GgChatWebhookUtil.call_webhook(content, chat_token[0].space_id, chat_token[0].key, chat_token[0].token)
        return ResponseModel(data=response)

    async def update_session(self, session_id:str, session_data: UpdateSessionModel, user_id:str) -> ResponseModel:
        updated_session = await self.session_repository.update_session(session_id, session_data.model_dump(exclude_unset=True))
        if not updated_session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)
        if user_id != updated_session.user_id:
            raise SessionException(SessionMessage.NOT_OWNER, SessionStatusCode.NOT_OWNER)
        logger.info('session update success with data: %s',updated_session)
        response = SessionResponse.model_validate(updated_session)
        await self._handle_response(response)
        return ResponseModel(data=response)
    async def delete_session(self, session_id:str):
        await self.session_repository.delete_session(session_id)
        return ResponseModel()

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
            await self._handle_response(response)
            list_sessions_response.append(response)
        return ResponsePaginatedModel(data=list_sessions_response, total=total, offset= filters.offset)

    async def get_session_by_id(self, session_id:str):
        session = await self.session_repository.get_session_by_id(session_id)
        if not session:
            raise SessionException(SessionMessage.NOT_FOUND, SessionStatusCode.NOT_FOUND)
        response = SessionResponse.model_validate(session)
        return ResponseModel(data=response)

    async def _handle_response(self, response:SessionResponse):
        # logger.info(f'response {response}')
        filter_task = FilterWorkItemModel(limit=10, offset=0,list_ids=response.list_task)
        # logger.info(f'filter_task: {filter_task}')
        list_tasks = await self.work_item_repository.filter_work_item_for_order(filter_task)
        list_task_res = []
        for task in list_tasks:
            list_task_res.append(TaskResponse.model_validate(task))
        response.list_tasks_data = list_task_res

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

    async def get_work_item_by_id(self, work_item_id:str, list_data: list):
        work_item = await self.work_item_repository.get_work_item_by_id(work_item_id)
        if work_item:
            list_data.append(work_item.title)

    async def remind_checkin(self):
        # get list session -> list user_id distinct checkin today
        # get list user not in list user_id
        # call api to remind
        start_of_today_vn = DateTimeUtil.get_start_time_today()
        logger.info(f"start_of_today_vn: %s{start_of_today_vn}")
        filters = FilterCheckInSessionModel(start_time=start_of_today_vn)
        list_user_id = await self.session_repository.get_all_sessions_checkin(filters)
        logger.info(f"list_user_id: %s{list_user_id}")

        list_user_not_checkin = await self.user_repository.get_all_user_not_match_id(list_user_id)

        logger.info(f"list_user_not_checkin: %s{list_user_not_checkin}")
        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=1)
        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        for user in list_user_not_checkin:
            if total > 0:
                content = FormatContentGgChatAPI.format_content_remind_checkin(user.name)
                GgChatWebhookUtil.call_webhook(content, chat_token[0].space_id, chat_token[0].key, chat_token[0].token)
        return

    async def remind_checkout(self):
        # get list session with end_time = None in today
        start_of_today_vn = DateTimeUtil.get_start_time_today()
        logger.info(f"start_of_today_vn: %s{start_of_today_vn}")

        filters = FilterCheckInSessionModel(start_time=start_of_today_vn, status=[SessionStatusEnum.NEW, SessionStatusEnum.IN_PROGRESS])

        list_user_id = await self.session_repository.get_all_sessions_checkin(filters)
        logger.info(f"list_user_id: %s{list_user_id}")


        list_user_name = await self.user_repository.get_all_user_match_id(list_user_id)
        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=1)
        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        for user in list_user_name:
            if total > 0:
                content = FormatContentGgChatAPI.format_content_remind_checkout(user.name)
                GgChatWebhookUtil.call_webhook(content, chat_token[0].space_id, chat_token[0].key, chat_token[0].token)
        return