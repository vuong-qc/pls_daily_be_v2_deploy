from pydantic import BaseModel

from src.enums.result_enum import ResultObjectType, ResultStatus, ResultType


class FilterResultModel(BaseModel):
    parent_id: str
    type: ResultType = ResultType.REPORT
    object_type: ResultObjectType | None = None
    object_ids: list[str] | None = None
    # status: ResultStatus | None = None
