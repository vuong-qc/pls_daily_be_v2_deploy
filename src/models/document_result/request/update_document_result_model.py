from typing import Optional

from pydantic import BaseModel
from src.enums.document_result_evaluate import DocumentResultEvaluate

class UpdateDocumentResult(BaseModel):
    owner_id: Optional[str] = None
    parent_id: Optional[str] = None
    evaluate: Optional[DocumentResultEvaluate] = None
    check: Optional[bool] = None