from typing import Union, Optional
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict

from src.enums.process_enum import ProcessPeriodType
from beanie import PydanticObjectId
from beanie.operators import Set
from pymongo.errors import DuplicateKeyError
from src.configs import settings
from src.models.section_result.section_result_document import SectionResultDocument
from src.models.user.user_document import UserDocument
from src.repositories.section_result.section_result_repository import SectionResultRepository
from src.utils.datetime_util import DateTimeUtil
from datetime import datetime, timedelta

_UNIT_MAP = {"DAY": "day", "WEEK": "week", "MONTH": "month", "QUARTER": "quarter"}
MAX_BUCKETS = 1000  # chặn range quá lớn


def _period_start(dt: datetime, period: ProcessPeriodType) -> datetime:
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == ProcessPeriodType.DAY:
        return dt
    if period == ProcessPeriodType.WEEK:  # tuần bắt đầu thứ Hai, khớp startOfWeek="monday"
        return dt - timedelta(days=dt.weekday())
    if period == ProcessPeriodType.MONTH:
        return dt.replace(day=1)
    # quarter: tháng 1, 4, 7, 10
    return dt.replace(month=(dt.month - 1) // 3 * 3 + 1, day=1)


def _add_months(dt: datetime, n: int) -> datetime:
    m = dt.month - 1 + n
    return dt.replace(year=dt.year + m // 12, month=m % 12 + 1, day=1)


def _next_period(dt: datetime, period: ProcessPeriodType) -> datetime:
    if period == ProcessPeriodType.DAY:
        return dt + timedelta(days=1)
    if period == ProcessPeriodType.WEEK:
        return dt + timedelta(days=7)
    if period == ProcessPeriodType.MONTH:
        return _add_months(dt, 1)
    return _add_months(dt, 3)


def generate_period_buckets(start: int, end: int, period: ProcessPeriodType) -> list[int]:
    """Danh sách timestamp (milli) đầu mỗi kỳ, theo giờ VN, từ kỳ chứa start đến kỳ chứa end."""
    cur = _period_start(datetime.fromtimestamp(start / 1000, ZoneInfo(settings.TZ)), period)
    last = _period_start(datetime.fromtimestamp(end / 1000, ZoneInfo(settings.TZ)), period)
    buckets: list[int] = []
    while cur <= last:
        buckets.append(int(cur.timestamp() * 1000))
        if len(buckets) > MAX_BUCKETS:
            raise ValueError("Khoảng thời gian quá lớn so với kiểu thống kê")
        cur = _next_period(cur, period)
    return buckets

class BeanieSectionResultRepository(SectionResultRepository):
    async def upsert_result(self, report_id: str, section_item_id: str, value: Union[float, str], created_by: str) -> tuple[SectionResultDocument, bool]:
        now = DateTimeUtil.current_milli_time()
        existing = await self.get_result(report_id, section_item_id)
        if existing:
            await existing.update(Set({"value": value, "updated_at": now}))
            return await self.get_result(report_id, section_item_id), False

        result = SectionResultDocument(
            report_id=report_id,
            section_item_id=section_item_id,
            value=value,
            created_by=created_by,
            creator_model=self._build_user_link(created_by),
            created_at=now,
            updated_at=now,
        )
        try:
            await result.insert()
            return await self.get_result(report_id, section_item_id), True
        except DuplicateKeyError:
            existing = await self.get_result(report_id, section_item_id)
            await existing.update(Set({"value": value, "updated_at": now}))
            return await self.get_result(report_id, section_item_id), False

    async def upsert_result_process(self, report_id:str, section_item_id: str, value: bool, created_by: str, date: int, note: Optional[str] = None) -> tuple[SectionResultDocument, bool]:
        now = DateTimeUtil.current_milli_time()
        existing = await self.get_result_process_date(report_id, section_item_id, date)
        if existing:
            await existing.update(Set({"value": value, "updated_at": now}))
            return await self.get_result_process_date(report_id, section_item_id, date), False

        result = SectionResultDocument(
            report_id=report_id,
            section_item_id=section_item_id,
            value=value,
            created_by=created_by,
            creator_model=self._build_user_link(created_by),
            created_at=now,
            updated_at=now,
            date=date,
            note= note
        )
        try:
            await result.insert()
            return await self.get_result_process_date(report_id, section_item_id, date, created_by), True
        except DuplicateKeyError:
            existing = await self.get_result_process_date(report_id, section_item_id, date, created_by)
            await existing.update(Set({"value": value, "updated_at": now}))
            return await self.get_result_process_date(report_id, section_item_id, date, created_by), False

    async def get_result(self, report_id: str, section_item_id: str) -> SectionResultDocument | None:
        return await SectionResultDocument.find_one(
            SectionResultDocument.report_id == report_id,
            SectionResultDocument.section_item_id == section_item_id,
            fetch_links=True,
        )
    async def get_result_process_date(self, report_id: str, section_item_id: str, date: int, user_id: str)-> SectionResultDocument | None:
        return await SectionResultDocument.find_one(
            SectionResultDocument.report_id == report_id,
            SectionResultDocument.section_item_id == section_item_id,
            SectionResultDocument.date == date,
            SectionResultDocument.created_by == user_id,
            fetch_links=True,
        )
    async def get_result_process(self, report_id: str, date: int, user_id: str) -> list[SectionResultDocument]:
        return await SectionResultDocument.find(
            SectionResultDocument.report_id == report_id,
            SectionResultDocument.date == date,
            SectionResultDocument.created_by == user_id,
            fetch_links=True,
        ).to_list()
    async def get_results_by_report(self, report_id: str) -> list[SectionResultDocument]:
        return await SectionResultDocument.find(
            SectionResultDocument.report_id == report_id,
            fetch_links=True,
        ).to_list()

    async def delete_results_by_report(self, report_id: str) -> None:
        results = await SectionResultDocument.find(
            SectionResultDocument.report_id == report_id,
        ).to_list()
        for result in results:
            await result.delete()

    async def count_bool_results_by_period(
            self,
            item_to_section: dict[str, str],
            start: int,
            end: int,
            period: ProcessPeriodType,
            user_id: str,
    ) -> list[dict]:
        if not item_to_section:
            return []

        total_by_section = Counter(item_to_section.values())
        total_items = sum(total_by_section.values())

        # 1. Khung kết quả
        buckets: dict[int, dict[str, dict]] = {
            bucket: {
                sid: {"count_check": 0, "count_uncheck": 0, "total": total}
                for sid, total in total_by_section.items()
            }
            for bucket in generate_period_buckets(start, end, period)
        }
        ratio_sum: dict[int, dict[str, float]] = {b: defaultdict(float) for b in buckets}

        # 2. Aggregate
        trunc: dict = {"unit": _UNIT_MAP[period], "timezone": settings.TZ}
        if period == ProcessPeriodType.WEEK:
            trunc["startOfWeek"] = "monday"

        pipeline = [
            {
                "$match": {
                    "section_item_id": {"$in": list(item_to_section.keys())},
                    "value": {"$type": "bool"},
                    "deleted_at": None,
                    "created_by": user_id,
                    "$or": [
                        {"date": {"$gte": start, "$lte": end}},
                        {"date": None, "created_at": {"$gte": start, "$lte": end}},
                    ],
                }
            },
            {"$addFields": {"eff_date": {"$ifNull": ["$date", "$created_at"]}}},
            {"$addFields": {"bucket": {"$toLong": {"$dateTrunc": {
                **trunc, "date": {"$toDate": "$eff_date"},
            }}}}},
            {
                "$group": {
                    "_id": {"bucket": "$bucket", "item": "$section_item_id"},
                    "check": {"$sum": {"$cond": [{"$eq": ["$value", True]}, 1, 0]}},
                    "uncheck": {"$sum": {"$cond": [{"$eq": ["$value", False]}, 1, 0]}},
                }
            },
        ]
        rows = await SectionResultDocument.aggregate(pipeline).to_list()

        # 3. Mỗi dòng là 1 item trong 1 kỳ: cộng dồn đếm, và cộng tỉ lệ của item
        for row in rows:
            section_id = item_to_section.get(row["_id"]["item"])
            bucket = row["_id"]["bucket"]
            if section_id is None or bucket not in buckets:
                continue
            check, uncheck = row["check"], row["uncheck"]
            stats = buckets[bucket][section_id]
            stats["count_check"] += check
            stats["count_uncheck"] += uncheck
            if check + uncheck:
                ratio_sum[bucket][section_id] += check / (check + uncheck)

        # 4. Phần trăm: tổng tỉ lệ item / tổng item
        result = []
        for bucket, sections in sorted(buckets.items()):
            for section_id, stats in sections.items():
                stats["percent"] = (
                    round(ratio_sum[bucket][section_id] / stats["total"] * 100, 2)
                    if stats["total"] else 0.0
                )
            average = (
                round(sum(ratio_sum[bucket].values()) / total_items * 100, 2)
                if total_items else 0.0
            )
            result.append({"date": bucket, "section": sections, "average_percent": average})
        return result
    def _build_user_link(self, user_id: str | None):
        if user_id and PydanticObjectId.is_valid(user_id):
            return UserDocument.model_construct(id=PydanticObjectId(user_id))
        return None
