import asyncio
import logging
from datetime import datetime

from src.repositories.chatbot_token.beanie_chatbot_token_repository import BeanieChatbotTokenRepository
from src.repositories.chatbot_token.chatbot_token_repository import ChatbotTokenRepository
from src.enums.chatbot_type_enum import ChatbotTypeEnum
from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel
from src.utils.form_text_gg_chat_api import FormatContentGgChatAPI
from src.utils.google_chat_webhook_util import GgChatWebhookUtil
from src.models.work_item.response.work_item_response_model import WorkItemResponse
from src.repositories.debounce_queue.debounce_queue_repository import DebounceQueueRepository

logger = logging.getLogger(__name__)
class DebouncedNotificationService:
    def __init__(self, chatbot_token_repo: ChatbotTokenRepository, debounce_queue_repository: DebounceQueueRepository):
        self.chatbot_token_repo = chatbot_token_repo
        self.debounce_queue_repository = debounce_queue_repository

    async def flush_due(self):
        async for meta, entries in self.debounce_queue_repository.pop_due():
            try:
                if meta.get("type") == "bug":
                    await self._send_bug(meta, entries)
            except Exception:
                logger.exception(f"Failed to flush due due for {meta}")

    async def _send_bug(self, meta:dict, entries: list[dict]):
        item = WorkItemResponse.model_validate(meta["item"])
        if not item.project:
            return
        # old_item của entry đầu tiên = trạng thái trước khi bắt đầu chuỗi sửa
        old_item = WorkItemResponse.model_validate(entries[0]["old_item"])
        content = FormatContentGgChatAPI.build_bug_updated_message(
            meta["user_name"], item, old_item, [e["changed_fields"] for e in entries]
        )
        filter_chat_token = FilterChatbotTokenModel(
            offset=0, limit=100, type=[ChatbotTypeEnum.BUG], position=[f"PROJECT_{item.project}"]
        )
        tokens, _ = await self.chatbot_token_repo.get_list_chatbot_tokens(filter_chat_token)
        format_div = FormatContentGgChatAPI.format_html_gg(content)
        for token in tokens:
            GgChatWebhookUtil.call_webhook(format_div, token.space_id, token.key, token.token)

def build_debounced_notification_service() -> DebouncedNotificationService:
    return DebouncedNotificationService(BeanieChatbotTokenRepository(), DebounceQueueRepository())