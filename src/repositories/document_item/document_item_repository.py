from abc import ABC, abstractmethod
from typing import Optional

from src.models.document_item.document_item_document import DocumentItem
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem

class DocumentItemRepository(ABC):
    @abstractmethod
    async def create_document(self, data: dict)-> DocumentItem:
        pass

    @abstractmethod
    async def update_document(self, document_id: str, data: UpdateDocumentItem)->None|DocumentItem:
        pass

    @abstractmethod
    async def delete_document(self, document_id: str):
        pass

    @abstractmethod
    async def get_list_document_items(self, filters: FilterDocumentItem)->tuple[list[DocumentItem], int]:
        pass
    @abstractmethod
    async def get_document_item(self, document_id: str) -> DocumentItem|None:
        pass
    @abstractmethod
    async def copy_document_items(self, filters: FilterDocumentItem, new_object_id:str):
        pass
    @abstractmethod
    async def count_completed_items_by_time_buckets(
            self,
            filters: FilterDocumentItem,
    ) -> dict: pass
    @abstractmethod
    async def count_items_by_time_buckets(
            self,
            filters: FilterDocumentItem,
    ) -> dict: pass
    async def get_all_document_items(self, filters: FilterDocumentItem) -> tuple[list[DocumentItem], int]:
        pass