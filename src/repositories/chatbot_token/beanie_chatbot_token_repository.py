from src.repositories.chatbot_token.chatbot_token_repository import ChatbotTokenRepository
from src.models.chatbot_token.chatbot_token_document import ChatbotTokenDocument
from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel

from beanie.operators import In, Set

class BeanieChatbotTokenRepository(ChatbotTokenRepository):
    async def create_chatbot_token(self,data: dict) -> ChatbotTokenDocument:
        chatbot_token = ChatbotTokenDocument(**data)
        return await chatbot_token.insert()

    async def update_chatbot_token(self,chatbot_token_id:str, data: dict) -> ChatbotTokenDocument | None:
        chatbot_token = await ChatbotTokenDocument.get(chatbot_token_id)
        if chatbot_token:
            await chatbot_token.update(Set(data))
            return chatbot_token
        return None

    async def delete_chatbot_token(self,chatbot_token_id:str):
        chatbot_token = await ChatbotTokenDocument.get(chatbot_token_id)
        if chatbot_token:
            await chatbot_token.delete()
        return None

    async def get_chatbot_token_by_id(self,chatbot_token_id:str) -> ChatbotTokenDocument | None:
        chatbot_token = await ChatbotTokenDocument.get(chatbot_token_id)
        return chatbot_token

    async def get_list_chatbot_tokens(self, filters : FilterChatbotTokenModel) -> tuple[list[ChatbotTokenDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop('offset',0)
        limit = filter_dump.pop('limit',10)

        if filters.type:
            filter_dump.update(
                In(ChatbotTokenDocument.type, filters.type)
            )

        if filters.position:
            filter_dump.update(
                In(ChatbotTokenDocument.position, filters.position)
            )

        query = ChatbotTokenDocument.find(filter_dump)
        count = await query.count()

        list_chatbot_tokens = await query.skip(offset).limit(limit).to_list()
        return list_chatbot_tokens, count