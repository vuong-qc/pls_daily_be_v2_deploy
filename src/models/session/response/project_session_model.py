from pydantic import BaseModel

class UserIdOnly(BaseModel):
    user_id: str