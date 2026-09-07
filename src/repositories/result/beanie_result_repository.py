from datetime import datetime, timezone

from beanie.operators import In, Set
from pymongo import UpdateOne

from src.enums.result_enum import ResultObjectType, ResultType
from src.models.result.request.create_result_model import CreateResultModel
from src.models.result.result_document import ResultDocument
from src.repositories.result.result_repository import ResultRepository
from src.utils.datetime_util import DateTimeUtil


class BeanieResultRepository(ResultRepository):
    async def upsert_many_result(self, data: list[CreateResultModel]) -> None:
        if not data:
            return
        operations = []

        for item in data:
            result_data = item.model_dump(mode="json")
            filters = {
                "parent_id": item.parent_id,
                "type": item.type,
                "object_id": item.object_id,
                "object_type": item.object_type,
            }
            operations.append(UpdateOne(
                filters,
                {
                    "$set": {
                        **result_data,
                        "deleted_at": None,
                        "updated_at": DateTimeUtil.current_milli_time(),
                    },
                    "$setOnInsert": {
                        "created_at": DateTimeUtil.current_milli_time(),
                    },
                },
                upsert=True,
            ))
        await ResultDocument.get_pymongo_collection().bulk_write(operations)

    async def add_close_result(self, parent_id: str, type: str, object_ids: list[str], user_id: str):
        pipeline_set = {
            "closed_by": {
                "$concatArrays": [
                    {
                        "$filter": {
                            # Nếu field chưa có (null), mặc định là mảng rỗng []
                            "input": {"$ifNull": ["$closed_by", []]},
                            "as": "user",
                            # Lọc bỏ phần tử trùng với user_id truyền vào (tránh add trùng)
                            "cond": {"$ne": ["$$user", user_id]}
                        }
                    },
                    [user_id]
                ]
            },
            "updated_at": DateTimeUtil.current_milli_time()
        }

        # update_many theo parent_id, type và object_id nằm trong danh sách object_ids
        await ResultDocument.find(
            {
                "parent_id": parent_id,
                "type": type,
                "object_id": {"$in": object_ids},
            }
        ).update([{"$set": pipeline_set}])



    async def remove_close_result(self, parent_id: str, type: str, object_ids: list[str], user_id: str):
        pipeline_set = {
            "closed_by": {
                "$filter": {
                    "input": {"$ifNull": ["$closed_by", []]},
                    "as": "user",
                    "cond": {"$ne": ["$$user", user_id]}
                }
            },
            "updated_at": DateTimeUtil.current_milli_time()
        }

        # update_many theo parent_id, type và object_id nằm trong danh sách object_ids
        await ResultDocument.find(
            {
                "parent_id": parent_id,
                "type": type,
                "object_id": {"$in": object_ids},
            }
        ).update([{"$set": pipeline_set}])

    async def get_results_by_report_id(self, report_id: str) -> list[ResultDocument]:
        return await ResultDocument.find(
            ResultDocument.parent_id == report_id,
            ResultDocument.type == ResultType.REPORT,
        ).to_list()

    async def delete_many_result(
            self, report_id: str, object_ids: list[str], object_type: ResultObjectType,
    ) -> None:
        if not object_ids:
            return
        await ResultDocument.find(
            ResultDocument.parent_id == report_id,
            ResultDocument.type == ResultType.REPORT,
            ResultDocument.object_type == object_type,
            In(ResultDocument.object_id, object_ids),
        ).update_many(Set({ResultDocument.deleted_at: datetime.now(timezone.utc)}))

    async def delete_many_result_by_report_id(self, report_id: str) -> None:
        await ResultDocument.find(
            ResultDocument.parent_id == report_id,
            ResultDocument.type == ResultType.REPORT,
        ).update_many(Set({ResultDocument.deleted_at: datetime.now(timezone.utc)}))
