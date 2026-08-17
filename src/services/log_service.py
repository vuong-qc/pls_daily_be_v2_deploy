from src.repositories.log.log_repository import LogRepository
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.models.log.request.create_log_model import CreateLogModel
from src.models.log.request.filter_log_model import FilterLogModel
from src.repositories.user.user_repository import UserRepository
class LogService:
    def __init__(self, repository: LogRepository, user_repository: UserRepository):
        self.repository = repository
        self.user_repository = user_repository

    async def create_log(self, log: CreateLogModel):
        created_log = await self.repository.create_log(log.model_dump())
        return ResponseModel(data=created_log)

    async def get_logs(self, filter_log: FilterLogModel) -> ResponsePaginatedModel:
        filter_log_dump = filter_log.model_dump(exclude_unset=True)
        list_log, total = await self.repository.get_list_logs(filter_log_dump)
        for log in list_log:
            user = await self.user_repository.get_user_by_id(log["user"])
            log["user"] = user
        return ResponsePaginatedModel(data=list_log, total=total, offset=filter_log.offset)