from enum import StrEnum, IntEnum
from fastapi import HTTPException, status

class TaskMessage(StrEnum):
    TASK_NOT_FOUND = "Task not found"
    SUBTASK_NOT_FOUND = "Subtask not found"
    NOT_HANDLER_PR0JECT = "Not handler project"
    DELETE_NOT_MATCH_TYPE = "Type Item must be TASK to be deleted"
    TASKER_NOT_MATCH_TASK = "Only tasker assigned to this task can create subtask"
    USER_TASK_PARENT_NOT_MATCH = 'Parent of user task must be BACKLOG'
    NOT_UPDATE_TASK_TYPE_IN_STORY = 'Can not change type of task belong story'
    NOT_CHANGE_TYPE_ITEM_HAS_CHILDREN = 'Can not change type of task/story has children'
    CANCELED_TASK = 'Canceled task'
class TaskStatusCode(IntEnum):
    TASK_NOT_FOUND = status.HTTP_404_NOT_FOUND
    SUBTASK_NOT_FOUND = status.HTTP_404_NOT_FOUND
    NOT_HANDLER_PR0JECT = status.HTTP_400_BAD_REQUEST
    DELETE_NOT_MATCH_TYPE = status.HTTP_400_BAD_REQUEST
    TASKER_NOT_MATCH_TASK = status.HTTP_400_BAD_REQUEST
    USER_TASK_PARENT_NOT_MATCH_TYPE = status.HTTP_400_BAD_REQUEST
    NOT_UPDATE_TASK_TYPE_IN_STORY = status.HTTP_400_BAD_REQUEST
    NOT_CHANGE_TYPE_ITEM_HAS_CHILDREN = status.HTTP_400_BAD_REQUEST
    CANCELED_TASK = status.HTTP_400_BAD_REQUEST

class TaskException(HTTPException):
    def __init__(self, message:TaskMessage, code: TaskStatusCode):
        super().__init__(
            status_code=code,
            detail=message
        )
