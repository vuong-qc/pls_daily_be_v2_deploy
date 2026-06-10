from src.models.session.request.filter_session_model import FilterSessionModel
from src.models.session.session_document import SessionDocument
from src.repositories.session.session_repository import SessionRepository
from beanie.operators import Set, In, LTE, GTE

class BeanieSessionRepository(SessionRepository):
    async def get_session_by_id(self, session_id: str) ->SessionDocument|None:
        session = await SessionDocument.get(session_id)
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
        
        query = SessionDocument.find(filter_dump)

        count = await query.count()

        list_session = await query.skip(offset).limit(limit).to_list()
        return list_session, count

    async def create_session(self, session: dict) -> SessionDocument:
        new_session = SessionDocument(**session)
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