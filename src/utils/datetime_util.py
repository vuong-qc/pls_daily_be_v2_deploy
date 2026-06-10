import time

class DateTimeUtil:
    @staticmethod
    def current_milli_time():
        return int(time.time() * 1000)
