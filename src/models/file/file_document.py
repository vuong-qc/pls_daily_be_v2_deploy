from beanie import Document
import pymongo
from datetime import datetime
from pydantic import Field
from typing import Optional

class FileDocument(Document):
    type: Optional[str] = None
    name: str
    status: str
    note: Optional[str] = None
    file_id: str
    thumbnail_id: Optional[str] = ""
    create_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    class Settings:
        name = "file"
        indexes =[
            [
                ("name", pymongo.TEXT),
            ],
        ]