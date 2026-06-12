from src.models.order.order_document import OrderDocument
from src.repositories.order.order_repository import OrderRepository
from src.utils.lexorank_util import LexorankUtil
import logging
logger = logging.getLogger(__name__)

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
        list_orders = await query.skip(offset).limit(limit).sort(+OrderDocument.order).to_list()
        return list_orders, count