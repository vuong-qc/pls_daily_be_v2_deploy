from typing import Optional

from pydantic import BaseModel
from src.enums.document_result_evaluate import DocumentResultEvaluate

class CreateDocumentResult(BaseModel):
    owner_id: Optional[str] = None
    parent_id: str
    evaluate: Optional[DocumentResultEvaluate] = None
    evaluate_todo: Optional[str] = None
    is_closed: Optional[bool] = False
