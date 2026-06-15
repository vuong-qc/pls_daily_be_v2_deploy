from beanie import PydanticObjectId

from src.models.session.request.filter_session_model import FilterSessionModel, FilterCheckInSessionModel
from src.models.session.session_document import SessionDocument
from src.models.user.user_document import UserDocument
from src.repositories.session.session_repository import SessionRepository
from beanie.operators import Set, In, LTE, GTE
from src.models.session.response.project_session_model import UserIdOnly

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
                GTE(SessionDocument.end_time, filter_dump.pop("start_time"))
            )
        if filters.end_time:
            filter_dump.update(
                LTE(SessionDocument.start_time, filter_dump.pop("end_time"))
            )
        
        query = SessionDocument.find(filter_dump, fetch_links=True)

        count = await query.count()

        list_session = await query.skip(offset).limit(limit).to_list()
        return list_session, count

    async def create_session(self, session: dict) -> SessionDocument:
        new_session = SessionDocument(**session)
        self._add_link_data(session, new_session)

        await new_session.insert()
        return new_session

    async def update_session(self, session_id:str, session_data: dict) -> SessionDocument | None:
        session = await SessionDocument.get(session_id)
        if session:
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
        query = SessionDocument.distinct(SessionDocument.user_id, filter_dump)
        return await query