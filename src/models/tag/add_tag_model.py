from pydantic import BaseModel, ConfigDict

class AddTagModel(BaseModel):
    tag_id: list[str]
    object_id: str
    type_object: str

