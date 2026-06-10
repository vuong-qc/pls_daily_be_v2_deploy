from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from bson import ObjectId


class FileRepository(ABC):
    @abstractmethod
    async def save(self, file): pass

    @abstractmethod
    async def get_by_name(self, file) -> Optional[Dict]: pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict]: pass

    @abstractmethod
    async def update(self, file) -> Optional[Dict]: pass

    @abstractmethod
    async def delete(self, file) -> None: pass

    @abstractmethod
    async def upload_from_stream(self, name: str, file: bytes): pass

    @abstractmethod
    async def open_download_stream(self, file_id: ObjectId): pass

    @abstractmethod
    async def update_thumbnail_id(self, record_id: str, thumbnail_id: str): pass

    @abstractmethod
    async def get_info_by_id(self, file_id: str): pass

    @abstractmethod
    async def get_info_files_by_ids(self, ids: list[str]):
        pass
