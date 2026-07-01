import httpx
from src.configs import settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import logging

logger = logging.getLogger(__name__)


# Tạo một hàm custom để đánh giá xem lỗi nào mới được phép retry
def is_retryable_exception(exception: Exception) -> bool:
    # 1. Nếu là lỗi HTTP Status (4xx, 5xx)
    if isinstance(exception, httpx.HTTPStatusError):
        status = exception.response.status_code
        # Chỉ retry khi Rate Limit (429) hoặc lỗi Server tạm thời (502, 503, 504)
        # Không retry với 400, 401, 403, 404 (sai logic client)
        if status in (429, 502, 503, 504):
            logger.warning(f"Retry do lỗi HTTP: {status}")
            return True
        return False

    # 2. Nếu là lỗi Mạng/Request
    if isinstance(exception, httpx.RequestError):
        # KHÔNG retry nếu là ReadTimeout hoặc WriteTimeout vì request CÓ THỂ đã tới server
        if isinstance(exception, (httpx.ReadTimeout, httpx.WriteTimeout)):
            logger.warning("Không retry vì lỗi Timeout (tránh duplicate)!")
            return False

            # CHỈ retry nếu là lỗi kết nối mạng (chắc chắn request chưa tới server)
        if isinstance(exception, (httpx.ConnectError, httpx.ConnectTimeout)):
            logger.warning("Retry do lỗi kết nối ban đầu.")
            return True

    return False


class GgChatWebhookUtil:
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        # Thay đổi từ retry_if_exception_type sang retry_if_exception với hàm custom
        retry=retry_if_exception(is_retryable_exception)
    )
    def call_webhook(payload: dict, space_id: str, key: str, token: str):
        url = f"{settings.GG_CHAT_API}/{space_id}/messages"
        query_params = {
            "key": key,
            "token": token,
        }

        # Có thể tăng timeout lên một chút nếu API của Google dạo này phản hồi chậm
        with httpx.Client(timeout=15.0) as client:
            logger.info(f"Đang gửi webhook tới space: {space_id}...")

            response = client.post(
                url=url,
                params=query_params,
                json=payload
            )

            response.raise_for_status()

            logger.info(f"Webhook gọi thành công! Status: {response.status_code}")
            return response.json()