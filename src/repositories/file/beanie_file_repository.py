from beanie import PydanticObjectId
from beanie.odm.operators.find.comparison import In
from fastapi import HTTPException
from src.repositories.file.file_repository import FileRepository
from typing import Optional, Dict
from src.models.file.file_document import FileDocument
from gridfs import AsyncGridFSBucket


class BeanieFileRepository(FileRepository):
    def __init__(self, db):
        print(type(db))
        fs = AsyncGridFSBucket(db)
        self.fs = fs

    async def save(self, file: FileDocument):
        await file.insert()
        return str(file.id)

    async def get_by_name(self, file) -> Optional[Dict]:
        pass

    async def get_by_id(self, id: str) -> Optional[Dict]:
        image = await FileDocument.get(id)
        return image

    async def update(self, file: FileDocument) -> Optional[Dict]:
        await file.save()
        data = file.model_dump()
        data['id'] = str(file.id)
        data.pop('file_id')
        return data

    async def delete(self, file):
        pass

    async def upload_from_stream(self, name: str, file: bytes):
        return await self.fs.upload_from_stream(name, file)

    async def open_download_stream(self, file_id: str):
        return await self.fs.open_download_stream(file_id)

    async def update_thumbnail_id(self, record_id: str, thumbnail_id: str):
        file_doc = await FileDocument.get(record_id)
        if not file_doc:
            print(f"CRITICAL: Không tìm thấy FileDocument với ID {record_id} để update thumbnail!")
            return False

        await file_doc.set({FileDocument.thumbnail_id: thumbnail_id})
        print(f"SUCCESS: Đã update thumbnail_id='{thumbnail_id}' cho record_id='{record_id}'")
        return True

    async def get_info_by_id(self, file_id: str):
        if not PydanticObjectId.is_valid(file_id):
            return None

        data = await FileDocument.get(file_id)

        if data:
            data_dump = data.model_dump()

            record_id_str = str(data_dump.pop('id'))

            data_dump['file_id'] = record_id_str

            data_dump['id'] = record_id_str

            if 'name' in data_dump:
                data_dump['file_name'] = data_dump.pop('name')
                data_dump['file_name'] = data_dump['file_name'] + "." + data_dump['type']

            return data_dump

        return None

    async def get_info_files_by_ids(self, ids: list[str]):
        valid_ids = [PydanticObjectId(i) for i in ids if PydanticObjectId.is_valid(i)]

        if not valid_ids:
            return []

        files = await FileDocument.find(
            In(FileDocument.id, valid_ids),
        ).to_list()

        results = []
        for data in files:
            data_dump = data.model_dump()

            record_id_str = str(data_dump.pop('id'))
            data_dump['id'] = record_id_str
            data_dump['file_id'] = record_id_str

            if 'name' in data_dump:
                name_val = data_dump.pop('name')
                file_type = data_dump.get('type', '')
                data_dump['file_name'] = f"{name_val}.{file_type}" if file_type else name_val

            results.append(data_dump)

        return results
