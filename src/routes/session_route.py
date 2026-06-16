from src.repositories.session.beanie_session_repository import BeanieSessionRepository
from src.repositories.work_item.beanie_work_item_repository import BeanieWorkItemRepository
from src.models.session.request.create_session_model import CreateSessionModel
from src.models.session.request.update_session_model import UpdateSessionModel, CheckoutModel
from src.models.session.request.filter_session_model import FilterSessionModel
from fastapi import APIRouter, Query, Depends, status, Header, HTTPException
from src.configs import settings
from src.repositories.user.beanie_user_repository import BeanieUserRepository
from src.constant.session_url_constant import SessionUrlEnum
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.services.session_service import SessionService
from typing import Annotated

from src.utils.proxy_util import get_current_user_by_token
from src.repositories.chatbot_token.beanie_chatbot_token_repository import BeanieChatbotTokenRepository
router = APIRouter(
    tags=['session'],
)

def get_session_service():
    session_repo = BeanieSessionRepository()
    work_item_repo = BeanieWorkItemRepository()
    chatbot_token_repo = BeanieChatbotTokenRepository()
    user_repo = BeanieUserRepository()
    return SessionService(session_repo, work_item_repo, chatbot_token_repo, user_repo)

@router.post('/checkin',
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             )
async def checkin(data: CreateSessionModel,
                  user_data: dict = Depends(get_current_user_by_token),
                  service: SessionService = Depends(get_session_service)
                  ):
    user_id = user_data.get('sub')
    data.user_id = user_id
    return await service.create_session(data)

@router.put('/update-session/{session_id}',
             status_code=status.HTTP_202_ACCEPTED,
            response_model=ResponseModel,
)
async def update_session(session_id:str,
                         data: UpdateSessionModel,
                         service: SessionService = Depends(get_session_service),
                         user_data: dict = Depends(get_current_user_by_token),
                         ):
    user_id = user_data.get('sub')
    return await service.update_session(session_id, data, user_id)
@router.get('/get-session/{session_id}',
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel,)
async def get_session(session_id:str,
                      service: SessionService = Depends(get_session_service),
                      user_data: dict = Depends(get_current_user_by_token),
                      ):
    return await service.get_session(session_id)

@router.get('/get-list-sessions',
             status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel
            )
async def get_list_sessions(
        filters: Annotated[FilterSessionModel, Query()],
        service: SessionService = Depends(get_session_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await service.get_list_sessions(filters)

@router.delete('/delete-session/{session_id}',

               status_code=status.HTTP_204_NO_CONTENT,)
async def delete_session(session_id:str,
                         service: SessionService = Depends(get_session_service),
                         user_data: dict = Depends(get_current_user_by_token),
                         ):
    return await service.delete_session(session_id)

@router.post('/checkout/{session_id}',
             status_code=status.HTTP_200_OK,
             response_model=ResponseModel,
             )
async def checkout(session_id:str,
                   data: CheckoutModel,
                   service: SessionService = Depends(get_session_service),
                   user_data: dict = Depends(get_current_user_by_token),
                   ):
    user_id = user_data.get('sub')
    return await service.checkout(user_id, session_id, data)

@router.post(f'/{SessionUrlEnum.REMIND_CHECKOUT.value}',
            include_in_schema=False
            )
async def not_checkout(
        x_internal_key: str = Header(),
        service: SessionService = Depends(get_session_service),
):
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,)
    # call service
    print('call success')
    return await service.remind_checkout()

@router.post(f'/{SessionUrlEnum.REMIND_CHECKIN.value}',
            include_in_schema=False
            )
async def not_checkin(
        x_internal_key: str = Header(),
        service: SessionService = Depends(get_session_service),
):
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,)
    # call service
    print('call success')
    return await service.remind_checkin()