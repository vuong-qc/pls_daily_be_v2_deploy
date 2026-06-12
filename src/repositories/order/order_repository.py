from abc import ABC, abstractmethod

from src.models.order.order_document import OrderDocument


class OrderRepository(ABC):
    @abstractmethod
    async def create_order(self, order: dict, prev_order:str | None, next_order:str | None) -> OrderDocument:
        pass
    @abstractmethod
    async def get_list_orders(self, filters: dict) -> tuple[list[OrderDocument], int]:
        pass
    @abstractmethod
    async def update_order(self, order_id: str, data: dict, prev_position: str, next_position: str) -> OrderDocument|None:
        pass