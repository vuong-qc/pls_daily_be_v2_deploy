from src.services.meeting_service import MeetingService
from src.repositories.meeting.beanie_meeting_repository import BeanieMeetingRepository
from src.repositories.document_item.beanie_document_item_repository import BeanieDocumentItemRepository
from src.routes.task_route import get_task_service, TaskService
from src.routes.document_route import get_document_service, DocumentItemService
from src.models.meeting.request.create_meeting_model import CreateMeetingModel
from src.models.meeting.request.update_meeting_model import UpdateMeetingModel
from src.models.meeting.request.filter_meeting_model import FilterMeetingModel
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.utils.proxy_util import get_current_user_by_token

router = APIRouter(
    tags=["Meeting"],
)
def get_meeting_service(task_service: TaskService = Depends(get_task_service),
                        document_service: DocumentItemService = Depends(get_document_service),
                        ):
    meet_repository = BeanieMeetingRepository()
    document_item_repository = BeanieDocumentItemRepository()
    return MeetingService(meet_repository, document_item_repository, task_service, document_service)

@router.post("/create-meeting",
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseModel,
             description="Create  new meeting",
             )
async def create_meeting(
        data: CreateMeetingModel,
        service: MeetingService = Depends(get_meeting_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data['sub']
    data.creator = user_id
    return await service.create_meeting(data)

@router.get("/get-list-meetings",
            status_code=status.HTTP_200_OK,
            response_model=ResponsePaginatedModel,
            description="Get list of meetings",
            )
async def get_list_meetings(
        query: Annotated[FilterMeetingModel, Query()],
        service: MeetingService = Depends(get_meeting_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    return await service.get_list_meetings(query)

@router.put("/update-meeting/{meeting_id}",
             status_code=status.HTTP_202_ACCEPTED,
             response_model=ResponseModel,
            description="Update  meeting",
)
async def update_meeting(
        meeting_id: str,
        data: UpdateMeetingModel,
        service: MeetingService = Depends(get_meeting_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data['sub']
    return await service.update_meeting(user_id, meeting_id, data)

@router.delete("/delete-meeting/{meeting_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               description="Delete  meeting",
               )
async def delete_meeting(
        meeting_id: str,
        service: MeetingService = Depends(get_meeting_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data['sub']
    return await service.delete_meeting(meeting_id, user_id)
@router.get("/get-meeting-todo-tasks",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel,
            description="Get list of tasks, todo, meeting",
            )
async def get_list_tasks(
        query: Annotated[FilterMeetingModel, Query()],
        service: MeetingService = Depends(get_meeting_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data['sub']
    return await service.get_meeting_todo_task(user_id,query)

@router.put("/attend-meeting/{meeting_id}",
             status_code=status.HTTP_202_ACCEPTED,
             response_model=ResponseModel,
            description="Attend meeting",)
async def attend_meeting(
        meeting_id: str,
        service: MeetingService = Depends(get_meeting_service),
        user_data: dict = Depends(get_current_user_by_token)
):
    user_id = user_data['sub']
    return await service.accept_meeting(meeting_id, user_id)