from typing import Optional

from pydantic import BaseModel


class CreateSectionModel(BaseModel):
    template_id: str
    prev_order: Optional[str] = None
    next_order: Optional[str] = None
    category: str


class CreateSectionItemModel(BaseModel):
    section_id: str
    prev_order: Optional[str] = None
    next_order: Optional[str] = None
    title: str
    description: Optional[str] = None
    value_type: str


class UpdateSectionModel(BaseModel):
    prev_order: Optional[str] = None
    next_order: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    value_type: Optional[str] = None
