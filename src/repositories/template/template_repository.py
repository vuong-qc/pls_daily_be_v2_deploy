from abc import ABC, abstractmethod
from src.models.template.template_document import TemplateDocument
from src.models.template.request.filter_template_model import FilterTemplateModel

class TemplateRepository(ABC):
    @abstractmethod
    async def create_template(self, data: dict) -> TemplateDocument:
        pass
    @abstractmethod
    async def update_template(self, template_id: str, data: dict) -> TemplateDocument:
        pass
    @abstractmethod
    async def delete_template(self, template_id: str) -> None:
        pass
    @abstractmethod
    async def get_template_by_id(self, template_id: str) -> TemplateDocument | None:
        pass
    @abstractmethod
    async def get_list_templates(self, filters: FilterTemplateModel) -> tuple[list[TemplateDocument], int]:
        pass