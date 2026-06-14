from src.models.order.order_document import OrderDocument
from src.repositories.order.order_repository import OrderRepository
from src.utils.lexorank_util import LexorankUtil
from beanie.operators import Set
import logging
logger = logging.getLogger(__name__)

class BeanieOrderRepository(OrderRepository):
    async def create_order(self, order: dict, prev_order_id:str | None, next_order_id:str | None) -> OrderDocument:
        order = OrderDocument(**order)
        prev_order = await OrderDocument.get(prev_order_id) if prev_order_id else None
        next_order = await OrderDocument.get(next_order_id) if next_order_id else None
        position = LexorankUtil.get_lexorank_between(prev_order, next_order)
        order.order = position
        await order.insert()
        logger.info(f"Created order with data: %s", order)
        return order

    async def get_list_orders(self, filters: dict) -> tuple[list[OrderDocument], int]:
        logger.info(f"Getting list of orders for filters: %s", filters)
        limit = filters.pop('limit', 10)
        offset = filters.pop('offset', 0)

        query = OrderDocument.find(filters)
        count = await query.count()
        list_orders = await query.skip(offset).limit(limit).sort(+OrderDocument.order).to_list()
        return list_orders, count

    async def update_order(self, order_id: str, data: dict, prev_order: str | None, next_order: str | None) -> OrderDocument|None:
        logger.info(f"Updating order: %s", order_id)
        logger.info(f"Updating order with data: %s", data)
        order = await OrderDocument.get(order_id)
        if order:
            position = LexorankUtil.get_lexorank_between(prev_order, next_order)
            data[OrderDocument.order] = position
            await order.update(Set(data))
            return order
        return None

    async def get_all_orders(self, filters: dict) -> list[OrderDocument]:
        logger.info(f"Getting list of orders for filters: %s", filters)
        limit = filters.pop('limit', 10)
        offset = filters.pop('offset', 0)
        query = OrderDocument.find(filters)
        count = await query.count()
        orders = await query.sort(+OrderDocument.order).to_list()
        return orders

    async def count_orders(self, filters: dict) -> int:
        logger.info(f"Getting list of orders for filters: %s", filters)
        limit = filters.pop('limit', 10)
        offset = filters.pop('offset', 0)
        query = OrderDocument.find(filters)
        count = await query.count()
        return count
    async def insert_many_orders(self, list_orders: list[dict]):
        list_doc_order = [OrderDocument(**order) for order in list_orders]
        await OrderDocument.insert_many(list_doc_order)

    async def find_one_order(self, filters: dict) -> OrderDocument | None:
        logger.info(f"Getting 1 order for filters: %s", filters)
        limit = filters.pop('limit', 10)
        offset = filters.pop('offset', 0)
        order = await OrderDocument.find_one(filters)
        return order