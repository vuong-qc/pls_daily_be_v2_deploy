from typing import Any

from pydantic import BaseModel


class MeetingTodoTaskResponseModel(BaseModel):
    meeting: Any
    task: Any
    todo: Any