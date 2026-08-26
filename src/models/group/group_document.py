from beanie import DocumentWithSoftDelete, Indexed, Link
from typing import Annotated, Optional
import pymongo
from src.models.user.user_document import UserDocument

class GroupDocument(DocumentWithSoftDelete):
    type: str
    sub_type: Optional[str] = None
    parent_id: Optional[str] = None
    parent_type: Optional[str] = None
    created_by: Optional[str] = None
    is_archived: Optional[bool] = None
    name: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    des: Optional[str] = None
    creator_model: Optional[Link[UserDocument]] = None

    class Settings:
        name="groups"
