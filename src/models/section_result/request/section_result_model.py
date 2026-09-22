from typing import Union, Optional

from pydantic import BaseModel


class UpsertSectionResultModel(BaseModel):
    value: Union[float, str, bool]

class UpsertResultProcessModel(BaseModel):
    note: Optional[str] = None
    value: bool
    date: int
    section_item_id: str

class FilterResultProcessModel(BaseModel):
    template_id: str
    user_id: str
    date: int

class FilterResultModel(BaseModel):
    start: int
    end: int
    template_id: str
    user_id: str