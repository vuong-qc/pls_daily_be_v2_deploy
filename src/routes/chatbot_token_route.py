from src.models.chatbot_token.request.create_chatbot_token_model import CreateChatbotToken
from src.models.chatbot_token.request.filter_chatbot_token_model import FilterChatbotTokenModel
from src.models.chatbot_token.request.update_chatbot_token_model import UpdateChatbotTokenModel
from src.repositories.chatbot_token.beanie_chatbot_token_repository import BeanieChatbotTokenRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.services.chatbot_token_service import ChatbotTokenService
from fastapi import FastAPI, APIRouter, Query, Depends, status
from typing import Annotated

from src.utils.proxy_util import get_current_user_by_token


def get_chatbot_service():
    chatbot_repo = BeanieChatbotTokenRepository()
    return ChatbotTokenService(chatbot_repo)

router = APIRouter(
    tags=["chatbot"],
)

@router.post("/create-chatbot-token",
            response_model=ResponseModel,
            summary='Store data necessary for webhook',
            status_code=status.HTTP_201_CREATED,
            )
async def create_chatbot_token(
        data: CreateChatbotToken,
        service: ChatbotTokenService = Depends(get_chatbot_service),
        user_data: dict= Depends(get_current_user_by_token)
):
    return await service.create_chatbot_token(data)

@router.put("/update-chatbot-token/{chatbot_token_id}",
            response_model=ResponseModel,
            summary='Update data necessary for webhook',
            status_code=status.HTTP_202_ACCEPTED
            )
async def update_chatbot_token(
        chatbot_token_id: str,
        update_date: UpdateChatbotTokenModel,
        service: ChatbotTokenService = Depends(get_chatbot_service),
        user_data: dict= Depends(get_current_user_by_token)
):
    return await service.update_chatbot_token(chatbot_token_id, update_date)

@router.get('/get-list-chatbot-tokens',
            response_model=ResponsePaginatedModel,
            summary='List chatbot tokens',
            status_code=status.HTTP_200_OK)
async def get_list_chatbot_tokens(
        query: Annotated[FilterChatbotTokenModel, Query()],
        service: ChatbotTokenService = Depends(get_chatbot_service),
        user_data: dict= Depends(get_current_user_by_token)
):
    return await service.get_list_chatbot_tokens(query)

@router.delete('/delete-chatbot-token/{chatbot_token_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               description='Delete chatbot token',
               )
async def delete_chatbot_token(
        chatbot_token_id: str,
        service: ChatbotTokenService = Depends(get_chatbot_service),
        user_data: dict= Depends(get_current_user_by_token)
):
    return await service.delete_chatbot_token(chatbot_token_id)