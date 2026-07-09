from src.enums.document_type_enum import DocumentTypeEnum
from src.models.document_item.request.create_document_item_model import CreateDocumentItem
from typing import Optional

class CreateTestcaseModel(CreateDocumentItem):
    object_id: str
    type: DocumentTypeEnum = DocumentTypeEnum.TC
    priority: Optional[str] = None
    notes: Optional[str] = None
    assignee: Optional[list[str]] = None
    sprint: Optional[str] = None
    task: Optional[str] = None
    precondition: Optional[str] = None
    step_implement: Optional[str] = None
    role: Optional[str] = None
    data_test: Optional[str] = None
    expect_result: Optional[str] = None
    final_result: Optional[str] = None
    handler: Optional[str] = None