from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.comment.comment_repository import CommentRepository
from src.models.comment.request.create_comment_model import CreateCommentModel
from src.models.comment.request.update_comment_model import UpdateCommentModel
from src.models.comment.request.filter_comment_model import FilterCommentModel
from src.models.comment.response.comment_response_model import CommentResponseModel
from src.services.user_service import UserService
import re
from beanie import PydanticObjectId
from src.exception.comment_exception import CommentException, CommentStatusCode, CommentMessage

class CommentService:
    def __init__(self, comment_repository: CommentRepository, user_service: UserService):
        self.comment_repository = comment_repository
        self.user_service = user_service

    async def create_comment(self, comment_model: CreateCommentModel) -> ResponseModel:
        if comment_model.parent_id:
            await self.get_comment_by_id(comment_model.parent_id)

        user_ids = self._extract_mentions(comment_model.content)
        raw_data = comment_model.model_dump(exclude_unset=True)
        raw_data["mentions"] = user_ids
        comment = await self.comment_repository.create_comment(raw_data)
        response = CommentResponseModel.model_validate(comment)
        return ResponseModel(data=response)
    async def update_comment(self, comment_id:str, comment_model: UpdateCommentModel) -> ResponseModel:
        if comment_model.content is None:
            return ResponseModel()
        user_ids = self._extract_mentions(comment_model.content)
        raw_data = comment_model.model_dump(exclude_unset=True)
        raw_data["mentions"] = user_ids
        comment = await self.comment_repository.update_comment(comment_id, raw_data)
        if not comment:
            raise CommentException(message= CommentMessage.NOT_FOUND, code= CommentStatusCode.NOT_FOUND)
        response = CommentResponseModel.model_validate(comment)
        return ResponseModel(data=response)

    async def get_comment_by_id(self, comment_id:str) -> ResponseModel:
        comment = await self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise CommentException(message= CommentMessage.NOT_FOUND, code= CommentStatusCode.NOT_FOUND)
        response = CommentResponseModel.model_validate(comment)
        return ResponseModel(data=response)

    async def get_list_comments(self, filters: FilterCommentModel)-> ResponsePaginatedModel:
        comments, total = await self.comment_repository.get_list_comments(filters)
        list_response = []
        for comment in comments:
            response = CommentResponseModel.model_validate(comment)
            list_response.append(response)
        return ResponsePaginatedModel(data=list_response, total=total, offset=filters.offset)

    async def delete_comment(self, comment_id:str, user_id :str):
        comment = await self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise CommentException(CommentMessage.NOT_FOUND, code= CommentStatusCode.NOT_FOUND)
        if comment.creator_id != user_id:
            raise CommentException(CommentMessage.NOT_CREATOR, code= CommentStatusCode.NOT_CREATOR)
        await self.comment_repository.delete_comment(comment_id)

    def _extract_mentions(self, content: str) -> list[str]:
        usernames = re.findall(r"@(\w+)", content)
        if not usernames:
            return []
        return [name for name in usernames if PydanticObjectId.is_valid(name)]
