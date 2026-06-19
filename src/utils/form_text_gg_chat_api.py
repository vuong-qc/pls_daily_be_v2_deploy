from datetime import datetime
from zoneinfo import ZoneInfo
from src.configs import settings
from src.enums.text_format_enum import TextFormatEnum

class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name: str, tasks: list[str], note: str) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        content = TextFormatEnum.CHECKIN.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name)

        # Build HTML text cho Task
        if tasks:
            task_list_str = TextFormatEnum.NEWLINE.join(f'{TextFormatEnum.TASK_PREFIX}{task}' for task in tasks)
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.NEWLINE}{task_list_str}"
        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.SPACE}{TextFormatEnum.TASK_EMPTY}"

        # Build HTML text cho Note
        note_line = f'{TextFormatEnum.TASK_PREFIX}{note}'

        # Nối tất cả lại bằng thẻ <br>
        full_html_text = TextFormatEnum.NEWLINE.join([
            content,
            task_lines,
            TextFormatEnum.NOTE,
            note_line
        ])

        # Trả về format Card V2 của Google Chat
        return {
            "cardsV2": [
                {
                    "cardId": f"checkin_{now_vn.timestamp()}",
                    "card": {
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": full_html_text  # Đưa đoạn HTML vào đây!
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

    @staticmethod
    def format_content_remind_checkin(user_name: str) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        content = TextFormatEnum.REMIND_CHECK_IN.format(user=user_name)
        return {
            "cardsV2": [
                {
                    "cardId": f"checkin_{now_vn.timestamp()}",
                    "card": {
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": content  # Đưa đoạn HTML vào đây!
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

    @staticmethod
    def format_content_remind_checkout(user_name: str) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        content = TextFormatEnum.REMIND_CHECK_OUT.format(user=user_name)
        return {
            "cardsV2": [
                {
                    "cardId": f"checkin_{now_vn.timestamp()}",
                    "card": {
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": content  # Đưa đoạn HTML vào đây!
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }