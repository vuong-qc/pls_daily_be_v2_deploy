from typing import Any

from pydantic import BaseModel


class MeetingTodoTaskResponseModel(BaseModel):
    meeting: Any
    task: Any
    todo: Any
    todo_department: Any

class MenuMeetingTodoTaskResponseModel(BaseModel):
    remaining_meeting: int
    remaining_task: int
    total_tasks: int
    total_done_tasks: int
    total_done_todo: int
    total_todo: int