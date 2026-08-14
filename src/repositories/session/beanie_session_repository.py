from beanie import PydanticObjectId
from zoneinfo import ZoneInfo
from src.models.session.request.filter_session_model import FilterSessionModel, FilterCheckInSessionModel, FilterSessionByDateRangeModel
from src.models.session.session_document import SessionDocument
from src.models.user.user_document import UserDocument
from src.repositories.session.session_repository import SessionRepository
from beanie.operators import Set, In, LTE, GTE
from src.configs import settings
from datetime import datetime
from src.utils.datetime_util import DateTimeUtil
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

    async def get_session_by_date_range(self, filters: FilterSessionByDateRangeModel):
        pipeline: list[dict] = [
            {
                "$match": {
                    "user_id": filters.user_id,
                    "id": {"$gte": filters.start_time, "$lte": filters.end_time},
                }
            }
        ]
        session_conditions = []
        if filters.checkin_late is not None:
            session_conditions.append({"$eq": ["$$s.checkin_late", filters.checkin_late]})
        if filters.checkout_late is not None:
            session_conditions.append({"$eq": ["$$s.checkout_late", filters.checkout_late]})
        if filters.arrival_status is not None:
            session_conditions.append({"$eq": ["$$s.arrival_status", filters.arrival_status]})
        if filters.departure_status is not None:
            session_conditions.append({"$eq": ["$$s.departure_status", filters.departure_status]})
        if filters.evaluate_session is not None:
            session_conditions.append({"$eq": ["$$s.evaluate_session", filters.evaluate_session]})
        if filters.work_form is not None:
            session_conditions.append({"$eq": ["$$s.work_form", filters.work_form]})

        if session_conditions:
            pipeline.append({
                "$addFields": {
                    "sessions": {
                        "$filter": {
                            "input": "$sessions",
                            "as" : "s",
                            "cond": {"$and": session_conditions},
                        }
                    }
                }
            })
            pipeline.append({"$addFields": {"total_sessions": {"$size": "$sessions"}}})

            pipeline.append({"$match": {"total_sessions": {"$gt": 0}}})

        pipeline.append({"$sort": {"id": -1}})

        results = await DailySessionView.aggregate(
            pipeline, projection_model=DailySessionView
        ).to_list()
        print("results: ",results)
        data_dict = {item.id: item for item in results}
        list_result = []
        all_dates = DateTimeUtil.generate_date_range(filters.start_time, filters.end_time)
        for date in all_dates:
            if date not in data_dict:
                list_result.append(DailySessionView(
                    id=date,
                    user_id=filters.user_id,
                    total_sessions=0,
                    sessions=[],
                ))
            else:
                list_result.append(data_dict[date])
        return list_result

