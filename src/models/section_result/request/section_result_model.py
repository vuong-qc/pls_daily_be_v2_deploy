from typing import Union

from pydantic import BaseModel


class UpsertSectionResultModel(BaseModel):
    value: Union[float, str]
    section_item_id: str