from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from typing import Optional

class FilterTaskModel(FilterWorkItemModel):
    type_order: Optional[str] = None
    parent: Optional[str] = None
