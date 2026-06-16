import time
from src.configs import settings
from zoneinfo import ZoneInfo
from datetime import datetime, time as time_datetime

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
