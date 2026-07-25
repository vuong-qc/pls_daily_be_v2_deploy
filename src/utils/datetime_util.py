import time
from src.configs import settings
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, time as time_datetime, date
from dateutil.relativedelta import relativedelta

class DateTimeUtil:
    @staticmethod
    def current_milli_time():
        return int(time.time() * 1000)
    @staticmethod
    def get_start_time_today():
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        start_of_today_vn = datetime.combine(now_vn.date(), time_datetime.min, tzinfo=tz_vn)

        return start_of_today_vn
    @staticmethod
    def generate_date_range(start_str: str, end_str: str) -> list[str]:
        dates = []
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        return dates

    @staticmethod
    def get_date_of_next_month(current_date: int, target_day: int) -> int:
        tz_vn = ZoneInfo(settings.TZ)

        date_month = datetime.fromtimestamp(current_date/1000, tz=tz_vn)
        next_month = date_month + relativedelta(months=+1, day=target_day)
        # convert other day
        weekday = next_month.weekday()

        # t7
        if weekday == 5:
            next_month -= timedelta(days=1)
        elif weekday == 6:
            next_month -= timedelta(days=2)

        return int(next_month.timestamp() * 1000)
