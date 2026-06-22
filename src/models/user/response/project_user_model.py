from pydantic import BaseModel

class ProjectUsername(BaseModel):
    name: str
    roles: list[int]