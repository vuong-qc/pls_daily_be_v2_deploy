from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from src.configs import settings
from src.enums.text_format_enum import TextFormatEnum
from src.models.task.response.task_response_model import TaskResponse

class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name: str, tasks: list[str], note: str, department: Optional[str]=None) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        content = TextFormatEnum.CHECKIN_DEPART.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name, department= department) if department else TextFormatEnum.CHECKIN.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name)

        # Build HTML text cho Task
        if tasks:
            task_list_str = TextFormatEnum.NEWLINE.join(f'{TextFormatEnum.TASK_PREFIX}{task}' for task in tasks)
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.NEWLINE}{task_list_str}"
        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.SPACE}{TextFormatEnum.TASK_EMPTY}"

        # Build HTML text cho Note
        cleaned_note = note.lstrip('-').strip()

        # Sau đó mới format với prefix
        note_line = f'{TextFormatEnum.TASK_PREFIX} {cleaned_note}'

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
    def format_content_checkout(user_name: str, tasks: list[TaskResponse], note: Optional[str]=None, department: Optional[str] = None) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        content = TextFormatEnum.CHECKOUT_DEPART.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name, department= department) if department else TextFormatEnum.CHECKOUT.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name)

        # Build HTML text cho Task
        task_blocks = []
        note_line = f'{TextFormatEnum.TASK_PREFIX}{note}' if note else ''
        if tasks:
            for task in tasks:
                # Header Task
                block = [
                    f"{TextFormatEnum.TASK_HEADER} {task.title}"
                ]

                # Subtask
                if task.children:
                    subtask_lines = TextFormatEnum.NEWLINE.join(
                        f"{TextFormatEnum.TASK_PREFIX}{sub.title}"
                        for sub in task.children
                    )

                    block.extend([
                        TextFormatEnum.SUBTASK_HEADER,
                        subtask_lines,
                    ])
                else:
                    block.append(
                        f"{TextFormatEnum.SUBTASK_HEADER} {TextFormatEnum.SUBTASK_EMPTY}"
                    )

                task_blocks.append(
                    TextFormatEnum.NEWLINE.join(block)
                )

            task_lines = TextFormatEnum.NEWLINE.join(task_blocks)

        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER} {TextFormatEnum.TASK_EMPTY}"
        # Nối tất cả lại bằng thẻ <br>
        full_html_text = TextFormatEnum.NEWLINE.join([
            content,
            task_lines,
            TextFormatEnum.RESULT_NOTE,
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