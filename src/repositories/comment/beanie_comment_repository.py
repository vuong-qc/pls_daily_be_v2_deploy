from beanie import PydanticObjectId
from beanie.operators import Set
from src.models.comment.comment_document import CommentDocument
from src.models.comment.request.filter_comment_model import FilterCommentModel
from src.repositories.comment.comment_repository import CommentRepository
from src.models.user.user_document import UserDocument

class BeanieCommentRepository(CommentRepository):
    async def create_comment(self, data: dict) -> CommentDocument:
        comment = CommentDocument(**data,
                                  creator= UserDocument.model_construct(id=PydanticObjectId(data.get("creator_id", "id"))),
                                  ancestors=[]
                                  )

        if data.get('parent_id') is not None:
            parent = await CommentDocument.find_one(CommentDocument.id == PydanticObjectId(data["parent_id"])).inc({CommentDocument.reply_count:1})
            if parent:
                parent = await CommentDocument.get(data['parent_id'])
                comment.ancestors = parent.ancestors + [data["parent_id"]]
            else:
                raise ValueError("Parent id is not found")
        await comment.insert()

        return await CommentDocument.find_one(CommentDocument.id == comment.id, fetch_links=True)

    async def update_comment(self, comment_id: str, data: dict) -> CommentDocument| None:
        CommentDocument.find_one(CommentDocument.id == PydanticObjectId(comment_id)).update(Set(data))
        return await CommentDocument.find_one(CommentDocument.id == PydanticObjectId(comment_id), fetch_links=True)
    async def delete_comment(self, comment_id: str) -> None:
        comment = await CommentDocument.get(comment_id)
        if comment:
            if comment.parent_id:
                await CommentDocument.find_one(CommentDocument.id == PydanticObjectId(comment.parent_id)).inc({CommentDocument.reply_count: -1})
            await comment.delete()
    async def get_list_comments(self, filters: FilterCommentModel) -> tuple[list[CommentDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", 0)
        limit = filter_dump.pop("limit", 10)
        query = CommentDocument.find(filter_dump, fetch_links=True)
        count = await query.count()
        list_comments = await query.sort(f"-{CommentDocument.created_at}").skip(offset).limit(limit).to_list()
        return list_comments, count

    async def get_comment_by_id(self, comment_id: str) -> CommentDocument| None:
        return await CommentDocument.find_one(CommentDocument.id == PydanticObjectId(comment_id), fetch_links=True)

