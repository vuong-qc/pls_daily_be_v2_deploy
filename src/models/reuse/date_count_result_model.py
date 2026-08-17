from pydantic import BaseModel
class DateCountResult(BaseModel):
    date: str
    count: int