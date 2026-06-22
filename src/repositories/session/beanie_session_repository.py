from beanie import PydanticObjectId
from zoneinfo import ZoneInfo
from src.models.session.request.filter_session_model import FilterSessionModel, FilterCheckInSessionModel
from src.models.session.session_document import SessionDocument
from src.models.user.user_document import UserDocument
from src.repositories.session.session_repository import SessionRepository
from beanie.operators import Set, In, LTE, GTE
from src.configs import settings
from datetime import datetime
from src.models.session.session_view import DailySessionView
import logging
logger = logging.getLogger(__name__)

class BeanieSessionRepository(SessionRepository):
    async def get_session_by_id(self, session_id: str) ->SessionDocument|None:
        session = await SessionDocument.get(session_id, fetch_links=True)
        return session

    async def get_list_session(self, filters: FilterSessionModel) -> tuple[list[SessionDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", 0)
        limit = filter_dump.pop("limit", 10)

        if filters.status:
            filter_dump.update(
                In(SessionDocument.status, filter_dump.pop("status")),
            )
        
        if filters.start_time:
            filter_dump.update(
                GTE(SessionDocument.start_time, filter_dump.pop("start_time"))
            )
        if filters.end_time:
            filter_dump.update(
                LTE(SessionDocument.end_time, filter_dump.pop("end_time"))
            )
        
        query = SessionDocument.find(filter_dump, fetch_links=True)

        count = await query.count()

        list_session = await query.sort(f"-{SessionDocument.start_time}").skip(offset).limit(limit).to_list()
        return list_session, count

    async def create_session(self, session: dict) -> SessionDocument:
        new_session = SessionDocument(**session)
        self._add_link_data(session, new_session)
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        new_session.checkin = now_vn > new_session.start_time
        await new_session.insert()
        return new_session

    async def update_session(self, session_id:str, session_data: dict) -> SessionDocument | None:
        session = await SessionDocument.find_one(SessionDocument.id==PydanticObjectId(session_id), fetch_links=True)
        if session:
            if session_data.get('end_time'):
                end_time = session_data.get('end_time')
                tz_vn = ZoneInfo(settings.TZ)
                now_vn = datetime.now(tz_vn)
                session_data['checkout'] = now_vn > end_time
            await session.update(Set(session_data))
            return session
        return None
    async def delete_session(self, session_id:str) -> None:
        session = await SessionDocument.get(session_id)
        if session:
            await session.delete()

    def _add_link_data(self, data: dict, session: SessionDocument):
        user_id: str | bool = data.get('user_id', False)
        if user_id:
            session.user = UserDocument.model_construct(id=PydanticObjectId(user_id))

    async def get_all_sessions_checkin(self, filters: FilterCheckInSessionModel)->list[str]:
        filter_dump = filters.model_dump(exclude_unset=True)
        filter_dump.update(
            GTE(SessionDocument.start_time,filter_dump.pop("start_time"))
        )
        if filters.status:
            filter_dump.update(
                In(SessionDocument.status, filter_dump.pop("status")),
            )
        logger.info('session today: %s',filter_dump)
        query = SessionDocument.distinct(SessionDocument.user_id, filter_dump)
        return await query

    async def get_session_by_date_range(self, user_id: str, start_date: str, end_date: str):
        results = await DailySessionView.find(
            DailySessionView.user_id == user_id,
            DailySessionView.id >= start_date,  # Lớn hơn hoặc bằng ngày bắt đầu
            DailySessionView.id <= end_date  # Nhỏ hơn hoặc bằng ngày kết thúc
        ).sort("-id").to_list()
        print("results: ",results)
        return results