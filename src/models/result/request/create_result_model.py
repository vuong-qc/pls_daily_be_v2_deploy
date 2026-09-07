from pydantic import BaseModel

from src.enums.result_enum import ResultObjectType, ResultStatus, ResultType


class CreateResultModel(BaseModel):
    parent_id: str
    type: ResultType
    object_id: str
    object_type: ResultObjectType
    # status: ResultStatus
