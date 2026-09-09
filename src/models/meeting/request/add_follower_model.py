from pydantic import BaseModel

class AddFollowerModel(BaseModel):
    list_user_ids: list[str]