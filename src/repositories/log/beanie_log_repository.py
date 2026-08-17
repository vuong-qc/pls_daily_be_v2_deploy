from src.repositories.log.log_repository import LogRepository
from beanie.operators import Set, And, GTE, LTE, In
from src.models.log.log_document import LogDocument
import re

class BeanieLogRepository(LogRepository):
    async def create_log(self, log: dict) -> dict:
        log = LogDocument(**log)
        await log.insert()
        log_dump = log.model_dump()
        log_dump["id"] = str(log_dump.pop("id"))
        return log_dump
    async def get_list_logs(self, filter_log: dict) -> tuple[list[dict], int]:
        offset = filter_log.pop("offset")
        limit = filter_log.pop("limit")
        if filter_log.get("text"):
            words = filter_log.pop("text").split()

            escaped_words = [re.escape(word) for word in words]
            safe_kw = r"\s+".join(escaped_words)
            print("safe_kw", safe_kw)
            filter_log["text"] = {"$regex": safe_kw, "$options": "i"}
        start = filter_log.pop("start", None)
        end = filter_log.pop("end", None)
        if start and end:
            filter_log.update(And(
                GTE(LogDocument.created_at, start),
                LTE(LogDocument.created_at, end),
            ))
        elif start:
            filter_log.update(GTE(LogDocument.created_at, start))
        elif end:
            filter_log.update(LTE(LogDocument.created_at, end))
        if filter_log.get("user"):
            filter_log.update(In(
                LogDocument.user, filter_log.pop("user")
            ))
        if filter_log.get("type"):
            filter_log.update(In(LogDocument.type, filter_log.pop("type")))
        if filter_log.get("action"):
            filter_log.update(In(LogDocument.action, filter_log.pop("action")))
        if filter_log.get("position"):
            filter_log.update(In(LogDocument.position, filter_log.pop("position")))
        if filter_log.get("object_id"):
            filter_log.update(In(LogDocument.object_id, filter_log.pop("object_id")))
        query = LogDocument.find(filter_log)
        count = await query.count()
        results = []
        list_log = await query.skip(offset).limit(limit).sort("-created_at").to_list(length=limit)
        for log in list_log:
            result = log.model_dump()
            result["id"] = str(result.pop("id"))
            results.append(result)
        return results, count


