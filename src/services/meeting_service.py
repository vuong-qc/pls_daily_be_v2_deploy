from src.models.meeting.meeting_document import MeetingDocument
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.meeting.meeting_repository import MeetingRepository
from src.models.meeting.response.meeting_response_model import MeetingResponse
from src.models.meeting.request.create_meeting_model import CreateMeetingModel
from src.models.meeting.request.update_meeting_model import UpdateMeetingModel
from src.models.meeting.request.filter_meeting_model import FilterMeetingModel
from src.enums.meeting_status_enum import MeetingStatusEnum
from src.enums.meeting_repeat_type import MeetingRepeatType
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.exception.meeting_exception import MeetingException, MeetingStatusCode, MeetingMessage
from src.repositories.document_item.document_item_repository import DocumentItemRepository
from src.enums.document_type_enum import DocumentTypeEnum
from src.utils.datetime_util import DateTimeUtil

class MeetingService:
    def __init__(self, meeting_repository: MeetingRepository, document_item_repository: DocumentItemRepository) -> None:
        self.meeting_repository = meeting_repository
        self.document_item_repository = document_item_repository

    async def create_meeting(self, data: CreateMeetingModel) -> ResponseModel:
        meeting = await self.meeting_repository.create_meeting(data.model_dump())
        response = MeetingResponse.model_validate(meeting)
        return ResponseModel(data=response)

    async def update_meeting(self, user_id:str, meeting_id: str, data: UpdateMeetingModel) -> ResponseModel:
        meeting = await self.meeting_repository.get_meeting_by_id(meeting_id)
        if not meeting:
            raise MeetingException(MeetingMessage.NOT_FOUND, MeetingStatusCode.NOT_FOUND)
        # check input
        if user_id != meeting.creator:
            raise MeetingException(MeetingMessage.NOT_OWNER, MeetingStatusCode.NOT_OWNER)
        repeat_type = meeting.repeat_type if data.repeat_type is None else data.repeat_type
        date_of_month = meeting.date_of_month if data.date_of_month is None else data.date_of_month
        if date_of_month is None and repeat_type == MeetingRepeatType.MONTHLY:
            raise MeetingException(MeetingMessage.REPEAT_TYPE_NOT_MATCH_DATE, MeetingStatusCode.REPEAT_TYPE_NOT_MATCH_DATE)
        if date_of_month and repeat_type != MeetingRepeatType.MONTHLY:
            raise MeetingException(MeetingMessage.REPEAT_TYPE_NOT_MATCH_DATE, MeetingStatusCode.REPEAT_TYPE_NOT_MATCH_DATE)

        if meeting.status == MeetingStatusEnum.DONE or meeting.status == MeetingStatusEnum.CANCELED:
            raise MeetingException(MeetingMessage.CURRENT_STATUS_CANT_CHANGE, MeetingStatusCode.CURRENT_STATUS_CANT_CHANGE)

        updated_meeting = await self.meeting_repository.update_meeting(meeting_id,data.model_dump(exclude_unset=True))
        if not updated_meeting:
            raise MeetingException(MeetingMessage.NOT_FOUND, MeetingStatusCode.NOT_FOUND)
        if meeting.status == MeetingStatusEnum.IN_PROGRESS and data.status and data.status == MeetingStatusEnum.DONE:
            # create new meeting
            await self._create_next_meeting(updated_meeting)

        response = MeetingResponse.model_validate(updated_meeting)
        return ResponseModel(data=response)

    async def delete_meeting(self, meeting_id: str, user_id: str):
        meeting = await self.meeting_repository.get_meeting_by_id(meeting_id)
        if not meeting:
            raise MeetingException(MeetingMessage.NOT_FOUND, MeetingStatusCode.NOT_FOUND)
        if user_id != meeting.creator:
            raise MeetingException(MeetingMessage.NOT_OWNER, MeetingStatusCode.NOT_OWNER)
        return await self.meeting_repository.delete_meeting(meeting_id)

    async def get_meeting(self, meeting_id: str):
        meeting = await self.meeting_repository.get_meeting_by_id(meeting_id)
        if not meeting:
            raise MeetingException(MeetingMessage.NOT_FOUND, MeetingStatusCode.NOT_FOUND)
        response = MeetingResponse.model_validate(meeting)
        return ResponseModel(data=response)

    async def get_list_meetings(self, filters: FilterMeetingModel) -> ResponsePaginatedModel:
        meetings, total = await self.meeting_repository.get_list_of_meetings(filters)
        list_meetings = []
        for meeting in meetings:
            response = MeetingResponse.model_validate(meeting)
            list_meetings.append(response)
        return ResponsePaginatedModel(data=list_meetings, total=total, offset=filters.offset)

    async def copy_document(self, meeting_id: str, new_meeting_id: str):
        # build filter document
        filters = FilterDocumentItem(offset=0, limit=1,type=[DocumentTypeEnum.MEETING_DOCUMENT], object_id=[meeting_id])
        await self.document_item_repository.copy_document_items(filters, new_meeting_id)

    async def _create_next_meeting(self, meeting: MeetingDocument):
        # calc the next date
        # create new doc
        new_meeting = meeting.model_copy(deep=True)
        if new_meeting.repeat_type == MeetingRepeatType.ONCE:
            return

        new_meeting.status = MeetingStatusEnum.NEW.value
        new_meeting.accepted_participant_ids = []
        new_meeting.notification_date = None
        if not new_meeting.parent_id:
            new_meeting.parent_id = str(meeting.id)
        if new_meeting.repeat_type == MeetingRepeatType.MONTHLY:
            new_meeting.meeting_date = DateTimeUtil.get_date_of_next_month(new_meeting.meeting_date, new_meeting.date_of_month)
        elif new_meeting.repeat_type == MeetingRepeatType.WEEKLY:
            next_7_day = 7*24*60*60*1000
            new_meeting.meeting_date = new_meeting.meeting_date + next_7_day

        data = new_meeting.model_dump()
        data.pop('id', None)
        new_data =await self.meeting_repository.create_meeting(data)
        await self.copy_document(str(new_meeting.id), str(new_data.id))