from pydantic import BaseModel

class ResponseFileModel(BaseModel):
    thumbnail_id:str = None
    file_id:str = None
    file_name: str = None