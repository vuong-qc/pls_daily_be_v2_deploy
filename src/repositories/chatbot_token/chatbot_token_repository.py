from abc import ABC, abstractmethod
from src.models.chatbot_token.chatbot_token_document import ChatbotTokenDocument
from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel

class ChatbotTokenRepository(ABC):
    @abstractmethod
    async def create_chatbot_token(self,data: dict) -> ChatbotTokenDocument:
        pass

    @abstractmethod
    async def update_chatbot_token(self,chatbot_token_id:str, data: dict) -> ChatbotTokenDocument | None:
        pass

    @abstractmethod
    async def delete_chatbot_token(self,chatbot_token_id:str):
        pass

    @abstractmethod
    async def get_chatbot_token_by_id(self,chatbot_token_id:str) -> ChatbotTokenDocument | None:
        pass

    @abstractmethod
    async def get_list_chatbot_tokens(self, filters : FilterChatbotTokenModel) -> tuple[list[ChatbotTokenDocument], int]:
        pass