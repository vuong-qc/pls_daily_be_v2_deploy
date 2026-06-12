from src.models.chatbot_token.response.chatbot_token_response_model import ChatbotTokenResponse
from src.models.chatbot_token.request.create_chatbot_token_model import CreateChatbotToken
from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel
from src.models.chatbot_token.request.update_chatbot_token_model import UpdateChatbotTokenModel
from src.repositories.chatbot_token.chatbot_token_repository import ChatbotTokenRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.exception.chatbot_token_exception import ChatbotTokenStatusCode, ChatbotTokenMessage, ChatbotTokenException

class ChatbotTokenService:
    def __init__(self, chatbot_token_repository: ChatbotTokenRepository):
        self.chatbot_token_repository = chatbot_token_repository

    async def create_chatbot_token(self, data: CreateChatbotToken):
        chatbot_token = await self.chatbot_token_repository.create_chatbot_token(data.model_dump())
        return ResponseModel(data=ChatbotTokenResponse.model_validate(chatbot_token))

    async def update_chatbot_token(self, chatbot_token_id:str, data: UpdateChatbotTokenModel):
        chatbot_token = await self.chatbot_token_repository.update_chatbot_token(chatbot_token_id, data.model_dump(exclude_unset=True))
        if not chatbot_token:
            raise ChatbotTokenException(ChatbotTokenMessage.NOT_FOUND, ChatbotTokenStatusCode.NOT_FOUND)
        return ResponseModel(data=ChatbotTokenResponse.model_validate(chatbot_token))

    async def delete_chatbot_token(self, chatbot_token_id:str):
        await self.chatbot_token_repository.delete_chatbot_token(chatbot_token_id)

    async def get_chatbot_token(self, chatbot_token_id:str):
        chatbot_token = await self.chatbot_token_repository.get_chatbot_token_by_id(chatbot_token_id)
        if not chatbot_token:
            raise ChatbotTokenException(ChatbotTokenMessage.NOT_FOUND, ChatbotTokenStatusCode.NOT_FOUND)
        return ResponseModel(data=ChatbotTokenResponse.model_validate(chatbot_token))

    async def get_list_chatbot_tokens(self, filters: FilterChatbotTokenModel):
        list_chatbot_tokens, total = await self.chatbot_token_repository.get_list_chatbot_tokens(filters)
        list_response = []
        for chatbot_token in list_chatbot_tokens:
            list_response.append(ChatbotTokenResponse.model_validate(chatbot_token))

        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)