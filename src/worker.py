import httpx
from src.configs import settings
from arq import cron
from arq.connections import RedisSettings
from zoneinfo import ZoneInfo
import logging
from src.constant.session_url_constant import SessionUrlEnum
logger = logging.getLogger(__name__)

# Đây là hàm chạy trong Worker
async def remind_forgot_checkout_task(ctx):
    logger.info("Bắt đầu gọi API nội bộ để lấy danh sách user quên checkout...")

    # URL nội bộ (ví dụ gọi trong cùng mạng LAN hoặc cùng Docker network)
    api_url = f'{settings.INTERNAL_API_URL}/{SessionUrlEnum.SESSIONS.value}/{SessionUrlEnum.REMIND_CHECKOUT.value}'
    headers = {
        "x-internal-key": settings.INTERNAL_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            # Gọi API của FastAPI
            await client.post(api_url, timeout=10.0, headers=headers)


        except httpx.HTTPError as e:
            logger.info(f"Lỗi khi gọi API nội bộ: {e}")

async def remind_checkin_task(ctx):
    logger.info('testing checkin...')
    headers = {
        "x-internal-key": settings.INTERNAL_API_KEY
    }
    api_url = f'{settings.INTERNAL_API_URL}/{SessionUrlEnum.SESSIONS.value}/{SessionUrlEnum.REMIND_CHECKIN.value}'
    async with httpx.AsyncClient() as client:
        try:
            await client.post(api_url, timeout=10.0, headers=headers)

        except httpx.HTTPError as e:
            logger.info('Error call api internal')

async def check_n_update_task(ctx):
    # query deadline < datetime current
    logger.info('testing check status task...')
    headers = {
        "x-internal-key": settings.INTERNAL_API_KEY
    }
    api_url = f'{settings.INTERNAL_API_URL}/task/{settings.SUB_DOMAIN_AUTO_UPDATE_TASK}'
    async with httpx.AsyncClient() as client:
        try:
            await client.post(api_url, timeout=10.0, headers=headers)

        except httpx.HTTPError as e:
            logger.info('Error call api internal')

class WorkerSettings:
    functions = []
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    # Định nghĩa lịch Cronjob
    cron_jobs = [
        # 1. Thông báo check-in: 9 giờ 30 phút, từ Thứ 2 (1) đến Thứ 6 (5)
        cron(remind_checkin_task, hour=settings.HOUR_CHECKIN_REMIND, minute=settings.MINUTE_CHECKIN_REMIND, weekday=settings.WEEKDAY_REMIND, ),
        # cron(remind_checkin_task, second=0),


        # 2. Thông báo quên checkout: 23 giờ 00 phút, tất cả các ngày trong tuần
        cron(remind_forgot_checkout_task, hour=settings.HOUR_CHECKOUT_REMIND, minute=settings.MINUTE_CHECKOUT_REMIND, weekday=settings.WEEKDAY_REMIND),
        # cron(remind_forgot_checkout_task, second=0)

        cron(check_n_update_task,hour=0, minute=0)
    ]