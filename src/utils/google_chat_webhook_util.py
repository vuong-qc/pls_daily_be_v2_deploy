import httpx
from src.configs import settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
logger = logging.getLogger(__name__)
class GgChatWebhookUtil:
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),  # retry max : 3
        wait=wait_exponential(multiplier=2, min=2, max=10),  # Chờ 2s, 4s, 8s
        #  retry khi gặp lỗi mạng (RequestError) hoặc lỗi HTTP 4xx, 5xx (HTTPStatusError)
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    def call_webhook(text: str, space_id: str, key: str, token: str):
        url = f"{settings.GG_CHAT_API}/{space_id}/messages"
        query_params = {
            "key": key,
            "token": token,
        }
        app_message = {
            "text": text
        }
        # url = f"{settings.GG_CHAT_API}/{space_id}/messages?key={key}&token={token}"
        # set timeout:10
        with httpx.Client(timeout=10.0) as client:
            logger.info(f"Đang gửi webhook tới space: {space_id}...")

            response = client.post(
                url=url,
                params=query_params,
                json=app_message  # Tự động dumps JSON và set Content-Type header
            )

            # Nếu API trả về mã lỗi (VD: 500 Internal Server Error, 502 Bad Gateway...)
            # Hàm này sẽ tự động raise lỗi httpx.HTTPStatusError để tenacity bắt và retry
            response.raise_for_status()

            logger.info(f"Webhook gọi thành công! Status: {response.status_code}")

            # Trả về data dạng Dictionary luôn nếu API trả về JSON
            return response.json()