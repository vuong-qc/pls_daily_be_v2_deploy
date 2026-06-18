from src.models.order.order_document import OrderDocument
from src.repositories.order.order_repository import OrderRepository
from src.utils.lexorank_util import LexorankUtil
from beanie.operators import Set
import logging
logger = logging.getLogger(__name__)
from pymongo import UpdateOne

class BeanieOrderRepository(OrderRepository):
    async def create_order(self, order: dict, prev_order:str | None, next_order:str | None) -> OrderDocument:
        order = OrderDocument(**order)
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
        list_orders = await query.skip(offset).limit(limit).sort(f'+{OrderDocument.order}').to_list()
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
        orders = await query.sort(f'+{OrderDocument.order}').to_list()
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
        if not list_doc_order:
            return None
        operations = []
        for order in list_orders:
            # Condition to find document
            filter_query = {
                f'{OrderDocument.owner_id}': order['owner_id'],
                f'{OrderDocument.object_id}': order['object_id'],
            }

            update_query = Set(order)

            operations.append(UpdateOne(filter_query, update_query, upsert=True))

        collection = OrderDocument.get_pymongo_collection()

        result = await collection.bulk_write(operations)
        return result

    async def find_one_order(self, filters: dict) -> OrderDocument | None:
        logger.info(f"Getting 1 order for filters: %s", filters)
        limit = filters.pop('limit', 10)
        offset = filters.pop('offset', 0)
        order = await OrderDocument.find_one(filters)
        return order