from abc import ABC, abstractmethod
from src.models.comment.comment_document import CommentDocument
from src.models.comment.request.filter_comment_model import FilterCommentModel

class CommentRepository(ABC):
    @abstractmethod
    async def create_comment(self, data: dict) -> CommentDocument:
        pass
    @abstractmethod
    async def update_comment(self, comment_id: str, data: dict) -> CommentDocument| None:
        pass
    @abstractmethod
    async def delete_comment(self, comment_id: str) -> None:
        pass
    @abstractmethod
    async def get_list_comments(self, filters: FilterCommentModel) -> tuple[list[CommentDocument], int]:
        pass
    @abstractmethod
    async def get_comment_by_id(self, comment_id: str) -> CommentDocument| None:
        pass