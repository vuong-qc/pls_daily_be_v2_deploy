from typing import Optional

from beanie import DocumentWithSoftDelete
class DocumentResult(DocumentWithSoftDelete):
    owner_id: Optional[str] = None
    parent_id: str
    evaluate: Optional[str] = None
    check: Optional[bool] = None

    class Settings:
        name='document_result'
        indexes = {
            'owner_id',
            'parent_id'
        }