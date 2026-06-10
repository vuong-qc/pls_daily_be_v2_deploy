from src.enums.document_type_enum import DocumentTypeEnum
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem


class FilterTestCaseModel(FilterDocumentItem):
    type: list[DocumentTypeEnum] = [DocumentTypeEnum.TC]
