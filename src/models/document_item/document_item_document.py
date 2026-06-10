from typing import Optional

from beanie import DocumentWithSoftDelete

class DocumentItem(DocumentWithSoftDelete):
    group_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    files: Optional[list[str]] = None
    type: str
    date_time: int
    object_id: Optional[str] = None
    parent_type: Optional[str] = None
    created_by: Optional[str] = None

    class Settings:
        name='document_items'