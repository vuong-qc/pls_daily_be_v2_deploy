from src.enums.document_type_enum import DocumentTypeEnum
from src.models.document_item.request.create_document_item_model import CreateDocumentItem

class CreateTestcaseModel(CreateDocumentItem):
    object_id: str
    type: DocumentTypeEnum = DocumentTypeEnum.TC