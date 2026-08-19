from src.models.user.user_document import UserDocument
from src.models.evaluate.evaluate_document import EvaluateDocument
from src.models.evaluate.request.filter_evaluate_model import FilterEvaluateModel
from src.repositories.evaluate.evaluate_repository import EvaluateRepository
from beanie import PydanticObjectId
from beanie.operators import In, Set, And, GTE, LTE

class BeanieEvaluateRepository(EvaluateRepository):
    async def create_evaluate(self, data: dict):
        document = EvaluateDocument(**data)
        self._add_link_document(data, document)
        await document.insert()
        return await EvaluateDocument.find_one(EvaluateDocument.id==document.id, fetch_links=True)

    async def update_evaluate(self, evaluate_id: str, data: dict) -> EvaluateDocument | None:
        evaluation = await EvaluateDocument.get(evaluate_id)
        if evaluation:
            self._add_link_document(data, evaluation)
            await evaluation.save()
            await evaluation.update(Set(data))
            return await EvaluateDocument.find_one(EvaluateDocument.id==evaluation.id, fetch_links=True)
        return None

    async def delete_evaluate(self, evaluate_id: str) -> None:
        evaluation = await EvaluateDocument.get(evaluate_id)
        if evaluation:
            await evaluation.delete()
        return

    async def get_evaluate_by_id(self, evaluate_id: str) -> EvaluateDocument | None:
        return await EvaluateDocument.find_one(EvaluateDocument.id==evaluate_id, fetch_links=True)

    async def get_list_evaluate(self, filter_evaluate_model: FilterEvaluateModel) -> tuple[list[EvaluateDocument], int]:
        filter_dump = filter_evaluate_model.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", 0)
        limit = filter_dump.pop("limit", 10)
        if filter_evaluate_model.assigned_id:
            filter_dump.update(
                In(EvaluateDocument.assigned_id, filter_dump.pop("assigned_id", None))
            )
        if filter_evaluate_model.creator_id:
            filter_dump.update(
                In(EvaluateDocument.creator_id, filter_dump.pop("creator_id", None))
            )
        if filter_evaluate_model.update_user:
            filter_dump.update(
                In(EvaluateDocument.update_user, filter_dump.pop("update_user", None))
            )
        start_time = filter_dump.pop("start_time", None)
        end_time = filter_dump.pop("end_time", None)
        if start_time and end_time:
            filter_dump.update(
                And(
                    GTE(EvaluateDocument.updated_at, start_time),
                    LTE(EvaluateDocument.updated_at, end_time),
                )
            )
        elif start_time:
            filter_dump.update(
                And(
                    GTE(EvaluateDocument.updated_at, start_time),
                )
            )
        elif end_time:
            filter_dump.update(
                And(
                    LTE(EvaluateDocument.updated_at, end_time),
                )
            )
        query = EvaluateDocument.find(filter_dump, fetch_links=True)
        count = await query.count()
        list_evaluate = await query.skip(offset).limit(limit).sort(f"{EvaluateDocument.updated_at}").to_list()
        return list_evaluate, count

    def _add_link_document(self, data: dict, doc: EvaluateDocument):
        creator_id: str | bool = data.get("creator_id", False)
        assigned_id: str | bool = data.get("assigned_id", False)
        update_user: str | bool = data.get("update_user", False)

        if type(creator_id) is not bool:
            if creator_id == "" or creator_id is None:
                doc.creator_model = None
            else:
                doc.creator_model = UserDocument.model_construct(id=PydanticObjectId(creator_id))

        if type(assigned_id) is not bool:
            if assigned_id == "" or assigned_id is None:
                doc.assigned_model = None
            else:
                doc.assigned_model = UserDocument.model_construct(id=PydanticObjectId(assigned_id))

        if type(update_user) is not bool:
            if update_user == "" or update_user is None:
                doc.updated_model = None
            else:
                doc.updated_model = UserDocument.model_construct(id=PydanticObjectId(update_user))