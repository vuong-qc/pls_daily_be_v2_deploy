from abc import ABC, abstractmethod

class LogRepository(ABC):
    @abstractmethod
    async def create_log(self, log: dict)->dict: pass
    @abstractmethod
    async def get_list_logs(self, filter_log: dict) -> tuple[list[dict], int]: pass