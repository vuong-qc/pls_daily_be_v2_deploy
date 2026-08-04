from abc import ABC, abstractmethod
from src.models.document_result.document_result_document import DocumentResult
from src.models.document_result.request.filter_document_result_model import FilterDocumentResult

class DocumentResultRepository(ABC):
    @abstractmethod
    async def get_document_result(self, document_id)->DocumentResult|None:
        pass

    @abstractmethod
    async def get_list_of_document_results(self, filters: FilterDocumentResult)-> tuple[list[DocumentResult], int]:
        pass

    @abstractmethod
    async def update_document_result(self, document_id:str, document_data: dict)->DocumentResult|None:
        pass

    @abstractmethod
    async def delete_document_result(self, document_id: str):
        pass

    @abstractmethod
    async def create_document_result(self, document_result: dict)->DocumentResult:
        pass

    @abstractmethod
    async def get_document_result_by_parent_id(self, parent_id: str, owner_id:str) ->DocumentResult|None:
        pass