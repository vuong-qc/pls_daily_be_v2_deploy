import asyncio
from typing import Optional

from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel
from src.repositories.chatbot_token.chatbot_token_repository import ChatbotTokenRepository
from src.enums.work_item_type import WorkItemType
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.repositories.user.user_repository import UserRepository
from src.models.work_item.request.create_work_item_model import CreateWorkItemModel
from src.models.work_item.request.update_work_item_model import UpdateWorkItemModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.models.work_item.response.work_item_response_model import WorkItemResponse
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.exception.work_item_exception import WorkItemException, WorkItemStatusCode, WorkItemMessage
from src.repositories.group.group_repository import GroupRepository
from src.models.group.response.group_reponse_model import GroupResponse
from src.utils.google_chat_webhook_util import GgChatWebhookUtil
from src.enums.chatbot_type_enum import ChatbotTypeEnum
from src.enums.text_format_enum import TextFormatEnum
from src.utils.form_text_gg_chat_api import FormatContentGgChatAPI
from src.enums.bug_status_enum import BugStatusEnum

import logging
logger = logging.getLogger(__name__)


class WorkItemService:
    def __init__(self, work_item_repository: WorkItemRepository,
                 group_repository: GroupRepository, user_repository: UserRepository,
                 chatbot_token_repository: ChatbotTokenRepository,
                 ):
        self.work_item_repository = work_item_repository
        self.group_repository = group_repository
        self.user_repository = user_repository
        self.chatbot_token_repository = chatbot_token_repository

    async def create_work_item_model(self, work_item_model: CreateWorkItemModel,  user_id:Optional[str] = None):
        work_item = await self.work_item_repository.create_work_item(work_item_model.model_dump())
        response = WorkItemResponse.model_validate(work_item)
        if work_item.type == WorkItemType.BUG:
            name = TextFormatEnum.GUEST
            if user_id:
                user = await self.user_repository.get_user_by_id(user_id)
                name = user.name

            content = FormatContentGgChatAPI.build_bug_new_message(name, response)
            if response.project:
                tokens = await self._get_tokens(ChatbotTypeEnum.BUG, self._convert_position(response.project))
                if tokens:
                    format_div = FormatContentGgChatAPI.format_html_gg(content)
                    for token in tokens:
                        GgChatWebhookUtil.call_webhook(format_div, token.space_id, token.key, token.token)

        await self._format_work_item_response(response)
        return ResponseModel(data=response)

    async def update_work_item_model(self, user_id:str, work_item_id:str, work_item_model: UpdateWorkItemModel):
        old_work_item_model = await self.work_item_repository.get_work_item_by_id(work_item_id)
        print("old_work_item_model", old_work_item_model)
        if not old_work_item_model:
            raise WorkItemException(WorkItemMessage.WORK_ITEM_NOT_FOUND, WorkItemStatusCode.WORK_ITEM_NOT_FOUND)
        work_item = await self.work_item_repository.update_work_item(work_item_id,work_item_model.model_dump(exclude_unset=True))
        if not work_item:
            raise WorkItemException(WorkItemMessage.WORK_ITEM_NOT_FOUND, WorkItemStatusCode.WORK_ITEM_NOT_FOUND)
        response = WorkItemResponse.model_validate(work_item)
        if work_item.type == WorkItemType.BUG:
            user = await self.user_repository.get_user_by_id(user_id)
            content = FormatContentGgChatAPI.build_bug_updated_message(user.name, response, WorkItemResponse.model_validate(old_work_item_model), work_item_model.model_dump(exclude_unset=True))
            if response.project:
                tokens = await self._get_tokens(ChatbotTypeEnum.BUG, self._convert_position(response.project))
                if tokens:
                    format_div = FormatContentGgChatAPI.format_html_gg(content)
                    for token in tokens:
                        GgChatWebhookUtil.call_webhook(format_div, token.space_id, token.key, token.token)


        await self._format_work_item_response(response)
        return ResponseModel(data=response)

    async def delete_work_item_model(self, user_id:str, work_item_id:str):
        work_item = await self.work_item_repository.get_work_item_by_id(work_item_id)
        if not work_item:
            raise WorkItemException(WorkItemMessage.WORK_ITEM_NOT_FOUND, WorkItemStatusCode.WORK_ITEM_NOT_FOUND)
        response = WorkItemResponse.model_validate(work_item)
        if work_item.type == WorkItemType.BUG:
            user = await self.user_repository.get_user_by_id(user_id)
            content = FormatContentGgChatAPI.build_bug_deleted_message(user.name, response)
            if response.project:
                tokens = await self._get_tokens(ChatbotTypeEnum.BUG, self._convert_position(response.project))
                if tokens:
                    format_div = FormatContentGgChatAPI.format_html_gg(content)
                    for token in tokens:
                        GgChatWebhookUtil.call_webhook(format_div, token.space_id, token.key, token.token)


        await self.work_item_repository.delete_work_item(work_item_id)
        return ResponseModel()

    async def list_work_item_model(self, filters: FilterWorkItemModel):
        work_items, total = await self.work_item_repository.get_list_work_items(filters)
        list_response = []
        for work_item in work_items:
            work_item_response = WorkItemResponse.model_validate(work_item)
            await self._format_work_item_response(work_item_response)
            list_response.append(work_item_response)
        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

    async def statistic_bug(self, filters: FilterWorkItemModel):
        result = await self.work_item_repository.statistic_bug(filters)
        return ResponseModel(data=result)

    async def _format_work_item_response(self, work_item_response: WorkItemResponse):
        logger.debug(f"DEBUG work_item_response: {work_item_response}")
        if work_item_response.group:
            group =  await self.group_repository.get_group_by_id(work_item_response.group)
            work_item_response.group_model = GroupResponse.model_validate(group) if group else None

        if work_item_response.sprint:
            sprint = await self.work_item_repository.get_work_item_by_id(work_item_response.sprint)
            work_item_response.sprint_model = WorkItemResponse.model_validate(sprint)

        if work_item_response.task:
            task = await self.work_item_repository.get_work_item_by_id(work_item_response.task)
            work_item_response.task_model = WorkItemResponse.model_validate(task) if task else None

        if work_item_response.project:
            project = await self.work_item_repository.get_work_item_by_id(work_item_response.project)
            work_item_response.project_model = WorkItemResponse.model_validate(project) if project else None
    def _convert_position(self, parent_id:str):
        return f"PROJECT_{parent_id}"

    async def _get_tokens(self, type_token: str, position:str):

        filter_chat_token = FilterChatbotTokenModel(offset=0, limit=100, type=[type_token], position=[position])

        chat_token, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filter_chat_token)
        return chat_token

    async def statistic_work_item(self, filters: FilterWorkItemModel):

        date_statistic_summary = await self.work_item_repository.statistic_in_date_range(filters, True)
        return ResponsePaginatedModel(data=date_statistic_summary, offset=filters.offset, total=len(date_statistic_summary))

    async def count_my_bugs(self, user_id: str):
        filters_summary= FilterWorkItemModel(offset=0, limit=10, handler_id=[user_id], type=[WorkItemType.BUG], assigned_id=[user_id], owner_id=[user_id])
        filters_fixed_summary = filters_summary.model_copy(deep=True)
        fix_status = [BugStatusEnum.FIXED, BugStatusEnum.VERIFIED]
        not_resolved_status = [BugStatusEnum.CONFIRMED, BugStatusEnum.FIXED, BugStatusEnum.NEW]
        filters_fixed_summary.status= fix_status
        filters_not_resolved_status_summary = filters_fixed_summary.model_copy(deep=True)
        filters_not_resolved_status_summary.status = not_resolved_status

        filters_assignee = FilterWorkItemModel(offset=0, limit=10, assigned_id=[user_id], type=[WorkItemType.BUG])
        filters_fixed_assignee = filters_assignee.model_copy(deep=True)
        filters_fixed_assignee.status = fix_status
        filters_not_resolved_status_assignee = filters_fixed_assignee.model_copy(deep=True)
        filters_not_resolved_status_assignee.status = not_resolved_status

        filters_handler = FilterWorkItemModel(offset=0, limit=10, handler_id=[user_id], type=[WorkItemType.BUG])
        filters_fixed_handler = filters_handler.model_copy(deep=True)
        filters_fixed_handler.status = fix_status
        filters_not_resolved_status_handler = filters_fixed_handler.model_copy(deep=True)
        filters_not_resolved_status_handler.status = not_resolved_status

        filters_owner = FilterWorkItemModel(offset=0, limit=10, owner_id=[user_id], type=[WorkItemType.BUG])
        filters_fixed_owner = filters_owner.model_copy(deep=True)
        filters_fixed_owner.status = fix_status
        filters_not_resolved_status_ower = filters_owner.model_copy(deep=True)
        filters_not_resolved_status_ower.status = not_resolved_status

        (
            summary, fix_summary, not_resolved_summary,
            assignee, fix_assignee, not_resolved_assignee,
            owner, fix_owner, not_resolved_owner,
            handler, fix_handler, not_resolved_handler,
         ) = await asyncio.gather(
            self.work_item_repository.count_work_items_or_logic(filters_summary),
            self.work_item_repository.count_work_items_or_logic(filters_fixed_summary),
            self.work_item_repository.count_work_items_or_logic(filters_not_resolved_status_summary),

            self.work_item_repository.count_work_items_or_logic(filters_assignee),
            self.work_item_repository.count_work_items_or_logic(filters_fixed_assignee),
            self.work_item_repository.count_work_items_or_logic(filters_not_resolved_status_assignee),

            self.work_item_repository.count_work_items_or_logic(filters_owner),
            self.work_item_repository.count_work_items_or_logic(filters_fixed_owner),
            self.work_item_repository.count_work_items_or_logic(filters_not_resolved_status_ower),

            self.work_item_repository.count_work_items_or_logic(filters_handler),
            self.work_item_repository.count_work_items_or_logic(filters_fixed_handler),
            self.work_item_repository.count_work_items_or_logic(filters_not_resolved_status_handler)
        )
        return ResponseModel(
            data={
                "summary": summary,
                "fix_summary": fix_summary,
                "not_resolved_summary": not_resolved_summary,
                "assignee": assignee,
                "fix_assignee": fix_assignee,
                "not_resolved_assignee": not_resolved_assignee,
                "owner": owner,
                "fix_owner": fix_owner,
                "not_resolved_owner": not_resolved_owner,
                "handler": handler,
                "fix_handler": fix_handler,
                "not_resolved_handler": not_resolved_handler,
            }
        )