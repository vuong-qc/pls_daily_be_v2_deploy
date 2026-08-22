from src.repositories.meeting.meeting_repository import MeetingRepository
from src.models.meeting.request.filter_meeting_model import FilterMeetingModel
from src.models.meeting.meeting_document import MeetingDocument
from src.models.user.user_document import UserDocument
from beanie import PydanticObjectId, UpdateResponse
from beanie.operators import Set, In, LTE, GTE, And, Or


class BeanieMeetingRepository(MeetingRepository):
    async def create_meeting(self, data: dict)-> MeetingDocument:
        meeting = MeetingDocument(**data)
        await self._add_link_document_item( data, meeting)
        await meeting.insert()
        return await MeetingDocument.find_one(MeetingDocument.id==PydanticObjectId(meeting.id), fetch_links=True)

    async def update_meeting(self, meeting_id: str, data: dict)-> MeetingDocument|None:
        meet = await MeetingDocument.find_one(MeetingDocument.id==PydanticObjectId(meeting_id), fetch_links=True)
        if meet:
            await self._add_link_document_item( data, meet )
            await meet.save()
            await meet.update(Set(data))
            return await MeetingDocument.find_one(MeetingDocument.id == PydanticObjectId(meeting_id), fetch_links=True)
        return None

    async def delete_meeting(self, meeting_id: str):
        meeting = await MeetingDocument.get(meeting_id)
        if meeting:
            await meeting.delete()

    async def get_list_of_meetings(self, filters: FilterMeetingModel) -> tuple[list[MeetingDocument],int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop('offset', 0)
        limit = filter_dump.pop('limit', 10)

        if filters.start_date and filters.end_date:
            filter_dump.update(
                And(
                    GTE(MeetingDocument.meeting_date, filter_dump.pop('start_date')),
                    LTE(MeetingDocument.meeting_date, filter_dump.pop('end_date'))
                )
            )
        elif filters.start_date:
            filter_dump.update(
                GTE(MeetingDocument.meeting_date, filter_dump.pop('start_date')),
            )
        elif filters.end_date:
            filter_dump.update(
                LTE(MeetingDocument.meeting_date, filter_dump.pop('end_date'))
            )

        if filters.participant_ids:
            filter_dump.update(
                In(MeetingDocument.participant_ids, filter_dump.pop('participant_ids')),
            )

        if filters.accepted_participant_ids:
            filter_dump.update(
                In(MeetingDocument.accepted_participant_ids, filter_dump.pop('accepted_participant_ids')),
            )

        if filters.handler:
            filter_dump.update(
                In(MeetingDocument.handler, filter_dump.pop('handler')),
            )
        join_user_ids = filter_dump.pop('is_in_meeting', [])
        if join_user_ids:
            filter_dump.update(
                Or(
                    In(MeetingDocument.participant_ids, join_user_ids),
                    In(MeetingDocument.creator, join_user_ids),
                    In(MeetingDocument.handler, join_user_ids),

                )
            )
        if filters.statuses:
            filter_dump.update(
                In(MeetingDocument.status, filter_dump.pop('statuses')),
            )
        # print("filter_dump", filter_dump)

        query = MeetingDocument.find(filter_dump, fetch_links=True)
        count = await query.count()
        list_meeting = await query.sort(f"+{MeetingDocument.meeting_date}").skip(offset).limit(limit).to_list()
        return list_meeting, count

    async def get_meeting_by_id(self, meeting_id: str)->MeetingDocument|None:
        return await MeetingDocument.get(meeting_id)

    async def add_participant(self, meeting_id: str, user_id:str)->MeetingDocument:
        pipeline_set = {

            # Logic cập nhật update_user bằng DB
            "accepted_participant_ids": {
                "$concatArrays": [
                    {
                        "$filter": {
                            # Nếu field chưa có (null), mặc định là mảng rỗng []
                            "input": {"$ifNull": ["$accepted_participant_ids", []]},
                            "as": "user",
                            # Lọc bỏ phần tử bị trùng với update_user truyền vào
                            "cond": {"$ne": ["$$user", user_id]}
                        }
                    },
                    # Nối thêm user_id vào cuối
                    [user_id]
                ]
            }
        }

        # 2. Thực thi lệnh update ngay trên DB (Truyền dưới dạng list để kích hoạt Pipeline Update)
        # Trả về document sau khi update
        await MeetingDocument.find_one(
            {"_id": PydanticObjectId(meeting_id)}
        ).update([{"$set": pipeline_set}])

        # Fetch lại document với fetch_links=True để resolve link đầy đủ
        meeting = await MeetingDocument.get(
            PydanticObjectId(meeting_id), fetch_links=True
        )
        return meeting

    async def remove_participant(self, meeting_id: str, user_id:str)->MeetingDocument:
        pipeline_set = {

            # Logic cập nhật update_user bằng DB
            "accepted_participant_ids": {
                "$concatArrays": [
                    {
                        "$filter": {
                            # Nếu field chưa có (null), mặc định là mảng rỗng []
                            "input": {"$ifNull": ["$accepted_participant_ids", []]},
                            "as": "user",
                            # Lọc bỏ phần tử bị trùng với update_user truyền vào
                            "cond": {"$ne": ["$$user", user_id]}
                        }
                    },
                    []
                ]
            }
        }

        # 2. Thực thi lệnh update ngay trên DB (Truyền dưới dạng list để kích hoạt Pipeline Update)
        # Trả về document sau khi update
        await MeetingDocument.find_one(
            {"_id": PydanticObjectId(meeting_id)}
        ).update([{"$set": pipeline_set}])

        # Fetch lại document với fetch_links=True để resolve link đầy đủ
        meeting = await MeetingDocument.get(
            PydanticObjectId(meeting_id), fetch_links=True
        )
        return meeting
    async def _add_link_document_item(self, data: dict, document: MeetingDocument):
        handler: list[str] | bool = data.get("handler", False)
        # print("handler_id",handler_id)
        # getattr(data,"owner_id", False)
        creator: str | bool = data.get("creator", False)


        participant_ids: list[str] | bool = data.get("participant_ids", False)

        if type(handler) is not bool:
            if handler == [] or handler is None:
                document.handler_models = []
            else:
                document.handler_models = [
                    UserDocument.model_construct(id=PydanticObjectId(uid))
                    for uid in handler if PydanticObjectId.is_valid(uid)
                ]


        if type(participant_ids) is not bool:
            if participant_ids == [] or participant_ids is None:
                document.participant_models = []
            else:
                document.participant_models = [
                    UserDocument.model_construct(id=PydanticObjectId(uid))
                    for uid in participant_ids if PydanticObjectId.is_valid(uid)
                ]

        if type(creator) is not bool:
            if creator is None or not PydanticObjectId.is_valid(creator):
                pass
            else:
                document.creator_model = UserDocument.model_construct(id=PydanticObjectId(creator))