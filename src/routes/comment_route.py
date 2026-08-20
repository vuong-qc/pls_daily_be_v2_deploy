from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.comment.request.create_comment_model import CreateCommentModel
from src.models.comment.request.update_comment_model import UpdateCommentModel
from src.models.comment.request.filter_comment_model import FilterCommentModel
from src.services.comment_service import CommentService
from src.repositories.comment.beanie_comment_repository import BeanieCommentRepository
from src.routes.user_route import get_user_service, UserService
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from src.utils.proxy_util import get_current_user_by_token

def get_comment_service(user_service: UserService = Depends(get_user_service)):
    comment_repo = BeanieCommentRepository()
    return CommentService(comment_repo, user_service)

router = APIRouter(
    tags=['comment'],
)

@router.post('/create-comment',
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             summary='Create a new comment',)
async def create_comment(
        comment: CreateCommentModel,
        service: CommentService = Depends(get_comment_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await service.create_comment(comment)

@router.put('/update-comment/{comment_id}',
            status_code=status.HTTP_202_ACCEPTED,
             response_model=ResponseModel,
            summary='Update a comment',)
async def update_comment(
        comment_id: str,
        comment: UpdateCommentModel,
        service: CommentService = Depends(get_comment_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await service.update_comment(comment_id, comment)

@router.delete('/delete-comment/{comment_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               summary='Delete a comment',)
async def delete_comment(
        comment_id: str,
        service: CommentService = Depends(get_comment_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    user_id= user_data.get("sub")
    return await service.delete_comment(comment_id, user_id)

@router.get('/list-comments',
            status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel,
            summary='List all comments',)
async def list_comments(
        query: Annotated[FilterCommentModel, Query()],
        service: CommentService = Depends(get_comment_service),
        user_data: dict = Depends(get_current_user_by_token),
):
    return await service.get_list_comments(query)