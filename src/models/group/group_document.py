from beanie import DocumentWithSoftDelete, Indexed
from typing import Annotated, Optional
import pymongo


class GroupDocument(DocumentWithSoftDelete):
    type: str
    sub_type: Optional[str] = None
    parent_id: Optional[str] = None
    parent_type: Optional[str] = None
    created_by: Optional[str] = None
    is_archived: Optional[bool] = None
    name: Annotated[str, Indexed(index_type=pymongo.TEXT)]

    class Settings:
        name="groups"
