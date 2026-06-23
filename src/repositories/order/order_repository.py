from abc import ABC, abstractmethod

from src.models.order.order_document import OrderDocument


class OrderRepository(ABC):
    @abstractmethod
    async def create_order(self, order: dict, prev_order_id:str | None, next_order_id:str | None) -> OrderDocument:
        pass
    @abstractmethod
    async def get_list_orders(self, filters: dict) -> tuple[list[OrderDocument], int]:
        pass
    @abstractmethod
    async def update_order(self, order_id: str, data: dict, prev_order_id: str | None, next_order_id: str | None) -> OrderDocument | None:
        pass

    @abstractmethod
    async def insert_many_orders(self, list_orders: list[dict]):
        pass

    @abstractmethod
    async def count_orders(self, filters: dict) -> int:
        pass

    @abstractmethod
    async def get_all_orders(self, filters: dict) -> list[OrderDocument]:
        pass

    @abstractmethod
    async def find_one_order(self, filters: dict) -> OrderDocument | None:
        pass
    @abstractmethod
    async def delete_order(self, order_id: str):
        pass