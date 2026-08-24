from fractional_indexing import generate_key_between

from src.models.order.request.filter_order_model import FilterOrderModel
from src.models.order.request.create_order_model import CreateOrderModel
import logging
from typing import TypeVar, Type
from pydantic import BaseModel
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.repositories.order.order_repository import OrderRepository
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

class LexorankUtil:

    @staticmethod
    def get_lexorank_between(prev_rank:str|None, next_rank:str|None) -> str:
        """Calculates lexically positioned between prev_rank and nex_rank."""
        return generate_key_between(
            prev_rank,
            next_rank,
        )
    @staticmethod
    async def auto_gen_order(filters: FilterOrderModel, filter_item: FilterWorkItemModel, response_model: Type[T],task_repository: WorkItemRepository, order_repository: OrderRepository)->tuple[list[T], int]:
        # check has any order
        # logger.info('check gen order')
        filters.offset = filter_item.offset
        filters.limit = filter_item.limit
        total = await order_repository.count_orders(filters.model_dump(exclude_unset=True))
        count_task = await task_repository.count_work_item(filter_item)
        list_response = []
        # logger.info('total order: %s', total)
        # logger.info('total task: %s', count_task)
        list_task = await task_repository.filter_work_item_for_order(
            filter_item)
        list_order = await order_repository.get_all_orders(filters.model_dump(exclude_unset=True))
        # use map to check miss order in case new task
        order_map = {o.object_id: o.order for o in list_order}
        list_new_order = []
        task_map = {}
        # get miss tasks and map
        missing_tasks = []
        for task in list_task:
            if str(task.id) not in order_map:
                missing_tasks.append(task)
            task_map[str(task.id)] = task
            logger.info('debug task: %s', task.title)

        missing_tasks = [task for task in list_task if str(task.id) not in order_map]
        current_position = list_order[0].order if total > 0 else None
        logger.debug('current_position: %s', current_position)

        for miss_task in missing_tasks:
            lexorank_position = LexorankUtil.get_lexorank_between(current_position, None)
            new_order = CreateOrderModel(object_id=str(miss_task.id), parent_id=miss_task.parent,
                                         owner_id=filters.owner_id, type=filter_item.type_order,
                                         order=lexorank_position)
            current_position = lexorank_position
            # add new order to list order
            list_order += [new_order]
            list_new_order.append(new_order.model_dump())

        if list_new_order:
            await order_repository.insert_many_orders(list_new_order)
        for order in list_order:
            task_doc = task_map.get(order.object_id)
            if task_doc:
                validate_task = response_model.model_validate(task_doc)
                validate_task.order = order.order
                list_response.append(validate_task)
            else:
                await order_repository.delete_order(str(order.id))
        # logger.info('list response with order: %s', list_response)
        list_response[:] = list_response[filter_item.offset:filter_item.offset + filter_item.limit]

        return list_response, count_task