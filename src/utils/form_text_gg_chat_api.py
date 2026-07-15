from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from src.configs import settings
from src.enums.text_format_enum import TextFormatEnum
from src.models.task.response.task_response_model import TaskResponse
from src.mappers.content_gg_chat_mapper import ARRIVAL_STATUS, DEPARTMENT_STATUS

class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name: str, tasks: list[str], note: str, department: Optional[list[str]]=None, start_time: Optional[datetime]= None, nickname: Optional[str] = None, checkin_late: Optional[bool]=None, arrival_status: Optional[str] = None, work_form: Optional[str] = None) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        if start_time and start_time.tzinfo is None:
            now_vn = start_time.replace(tzinfo=tz_vn)

            # Trường hợp 2: end_time đã có timezone (ví dụ FE gửi lên là UTC)
        elif start_time:
            now_vn = start_time.astimezone(tz_vn)
        if nickname:
            user_name = f"{user_name} ({nickname})"
        content = TextFormatEnum.CHECKIN_DEPART.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name, department= department) if department else TextFormatEnum.CHECKIN.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name)
        first_line = ""
        if checkin_late is not None:
            first_line = f"[{TextFormatEnum.CHECKIN_LATE}]"
        if arrival_status is not None:
            first_line = first_line + TextFormatEnum.TASK_PREFIX+ f"[{ARRIVAL_STATUS.get(arrival_status)}]"
        if work_form is not None:
            first_line = first_line + TextFormatEnum.TASK_PREFIX + work_form
        # Build HTML text cho Task
        if tasks:
            task_list_str = TextFormatEnum.NEWLINE.join(f'{TextFormatEnum.TASK_PREFIX}{task}' for task in tasks)
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.NEWLINE}{task_list_str}"
        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.SPACE}{TextFormatEnum.TASK_EMPTY}"

        # Build HTML text cho Note
        cleaned_note = note.lstrip('-').strip()

        # Sau đó mới format với prefix
        note_line = f'{cleaned_note}'

        # Nối tất cả lại bằng thẻ <br>
        full_html_text = TextFormatEnum.NEWLINE.join([
            first_line,
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
    def format_content_checkout(user_name: str, tasks: list[TaskResponse], note: Optional[str]=None, department: Optional[list[str]] = None, end_time: Optional[datetime]= None, nickname: Optional[str] = None, checkout_late: Optional[bool] = None, departure_status:Optional[str] = None) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        if end_time and end_time.tzinfo is None:
            now_vn = end_time.replace(tzinfo=tz_vn)

            # Trường hợp 2: end_time đã có timezone (ví dụ FE gửi lên là UTC)
        elif end_time:
            now_vn = end_time.astimezone(tz_vn)
        if nickname:
            user_name = f"{user_name} ({nickname})"
        content = TextFormatEnum.CHECKOUT_DEPART.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name, department= department) if department else TextFormatEnum.CHECKOUT.format(time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name)

        # Build HTML text cho Task
        task_blocks = []
        note_line = f'{TextFormatEnum.TASK_PREFIX}{note}' if note else ''
        if tasks:
            for task in tasks:
                # Header Task
                block = [
                    f"{TextFormatEnum.TASK_HEADER} {task.title} [{task.status}] {task.estimated_point}"
                ] if task.estimated_point else [
                    f"{TextFormatEnum.TASK_HEADER} {task.title} [{task.status}] {TextFormatEnum.SUBTASK_NOT_DONE}"
                ]

                # # Subtask
                # if task.children:
                #     subtask_lines = TextFormatEnum.NEWLINE.join(
                #         f"{TextFormatEnum.TASK_PREFIX}{sub.title}"
                #         for sub in task.children
                #     )
                #
                #     block.extend([
                #         TextFormatEnum.SUBTASK_HEADER,
                #         subtask_lines,
                #     ])
                # else:
                #     block.append(
                #         f"{TextFormatEnum.SUBTASK_HEADER} {TextFormatEnum.SUBTASK_EMPTY}"
                #     )

                task_blocks.append(
                    TextFormatEnum.NEWLINE.join(block)
                )

            task_lines = TextFormatEnum.NEWLINE.join(task_blocks)

        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER} {TextFormatEnum.TASK_EMPTY}"
        first_line = ""
        if checkout_late is not None:
            first_line = f"[{TextFormatEnum.CHECKOUT_LATE}]"
        if departure_status is not None:
            first_line = first_line + TextFormatEnum.TASK_PREFIX + f"[{DEPARTMENT_STATUS.get(departure_status)}]"
        # Nối tất cả lại bằng thẻ <br>
        full_html_text = TextFormatEnum.NEWLINE.join([
            first_line,
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