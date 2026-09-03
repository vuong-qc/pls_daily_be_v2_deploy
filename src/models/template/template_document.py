from typing import Optional, Annotated

from pydantic import Field

from src.enums.template_status_enum import TemplateStatusEnum
import pymongo
from beanie import DocumentWithSoftDelete, Link, Indexed

from src.models.user.user_document import UserDocument
from src.utils.datetime_util import DateTimeUtil


class TemplateDocument(DocumentWithSoftDelete):
    group: str
    created_by: str
    creator_model: Optional[Link[UserDocument]] = None
    position: Optional[str] = None
    title: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    description: Optional[str] = None
    status: str = TemplateStatusEnum.DRAFT
    created_at: int = Field(default_factory=DateTimeUtil.current_milli_time)
    updated_at: int = Field(default_factory=DateTimeUtil.current_milli_time)

    class Settings:
        name = "templates"