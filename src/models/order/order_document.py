from beanie import DocumentWithSoftDelete, Indexed
import pymongo
from pymongo import IndexModel


class OrderDocument(DocumentWithSoftDelete):
    type: str
    object_id: str
    owner_id: str
    order: str
    parent_id: str

    class Settings:
        name='order'
        indexes=[
            IndexModel(
                [
                    ('object_id', pymongo.ASCENDING),
                    ('owner_id', pymongo.ASCENDING),
                    ('parent_id', pymongo.ASCENDING),
                    ('type', pymongo.ASCENDING),
                ],
                name='idx_owner_type_order'
            ),
            IndexModel(
                [
                    ('owner_id', pymongo.ASCENDING),
                    ('object_id', pymongo.ASCENDING),
                ],
                unique=True,  # Kích hoạt tính năng duy nhất
                partialFilterExpression={"deleted_at": None},
            )
        ]