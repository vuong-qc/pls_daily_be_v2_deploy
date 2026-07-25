from datetime import datetime
from typing import Optional, Any
from zoneinfo import ZoneInfo
from src.configs import settings
from src.enums.text_format_enum import TextFormatEnum
from src.models.task.response.task_response_model import TaskResponse
from src.models.work_item.response.work_item_response_model import WorkItemResponse
from src.mappers.content_gg_chat_mapper import ARRIVAL_STATUS, DEPARTMENT_STATUS, BUG_TYPE, FIELD_LABEL_MAP
import hashlib


class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name: str, tasks: list[str], note: str, department: Optional[list[str]]=None, start_time: Optional[datetime]= None, nickname: Optional[str] = None, checkin_late: Optional[bool]=False, arrival_status: Optional[str] = None, work_form: Optional[str] = None) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        if start_time and start_time.tzinfo is None:
            now_vn = start_time.replace(tzinfo=tz_vn)

            # Trường hợp 2: end_time đã có timezone (ví dụ FE gửi lên là UTC)
        elif start_time:
            now_vn = start_time.astimezone(tz_vn)
        if nickname:
            user_name = f"{user_name} ({nickname})"

        # Build department text: mỗi phòng ban tô xanh lá, nối bằng dấu •


        content = TextFormatEnum.CHECKIN.format(
                time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name
            )

        if department:
            # Nối các phòng ban bằng NEWLINE để mỗi phòng ban xuống 1 dòng
            department_text = TextFormatEnum.NEWLINE.join(
                TextFormatEnum.DEPARTMENT_ITEM.format(department=dep) for dep in department
            )

            # Ghép chữ "Phòng ban:" với danh sách phòng ban ở dưới
            department_lines = f"{TextFormatEnum.DEPARTMENT_HEADER}{TextFormatEnum.NEWLINE}{department_text}"

            # Đưa toàn bộ block phòng ban xuống dưới content chính
            content = TextFormatEnum.NEWLINE.join([content, department_lines])
        first_line = ""
        if checkin_late:
            first_line = f"[{TextFormatEnum.CHECKIN_LATE}]"
        else:
            first_line = f"[{TextFormatEnum.CHECKIN_ON_TIME}]"
        if arrival_status is not None:
            first_line = first_line + TextFormatEnum.TASK_PREFIX+ f"[{ARRIVAL_STATUS.get(arrival_status)}]"
        if work_form is not None:
            first_line = first_line + TextFormatEnum.TASK_PREFIX + f"[{work_form}]"
        # Build HTML text cho Task
        if tasks:
            task_list_str = TextFormatEnum.NEWLINE.join(f'{TextFormatEnum.TASK_PREFIX}{task}' for task in tasks)
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.NEWLINE}{task_list_str}"
        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER}{TextFormatEnum.SPACE}{TextFormatEnum.TASK_EMPTY}"


        lines = note.split('\n')

        formatted_lines = []
        for line in lines:
            # Bước 1: Dùng .strip() để xóa khoảng trắng 2 đầu (đề phòng có dấu cách trước dấu -)
            # Bước 2: Dùng .lstrip('-') để xóa các dấu '-' ở đầu
            # Bước 3: Dùng .strip() lần nữa để xóa khoảng trắng bị kẹt giữa dấu '-' và chữ (vd: "- aa" -> "aa")
            cleaned_note = line.strip().lstrip('-').strip()

            # Bước 4: Gắn prefix vào đầu dòng (chỉ xử lý nếu dòng đó có nội dung)
            if cleaned_note:
                note_line = f'{TextFormatEnum.TASK_PREFIX}{cleaned_note}'
                formatted_lines.append(note_line)

        # Ghép các dòng lại thành một chuỗi duy nhất, cách nhau bởi ký tự xuống dòng
        output_text = '\n'.join(formatted_lines)
        # # Build HTML text cho Note
        # cleaned_note = note.lstrip('-').strip()
        #
        # # Sau đó mới format với prefix
        # note_line = f'{cleaned_note}'
        note_line = output_text

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
    def format_content_checkout(user_name: str, tasks: list[TaskResponse], note: Optional[str] = None,
                                department: Optional[list[str]] = None, end_time: Optional[datetime] = None,
                                nickname: Optional[str] = None, checkout_late: Optional[bool] = False,
                                departure_status: Optional[str] = None, work_form: Optional[str] = None,
                                evaluate: Optional[str] = None
                                ) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        if end_time and end_time.tzinfo is None:
            now_vn = end_time.replace(tzinfo=tz_vn)
        elif end_time:
            now_vn = end_time.astimezone(tz_vn)
        if nickname:
            user_name = f"{user_name} ({nickname})"
        content = TextFormatEnum.CHECKOUT.format(
                time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name
            )

        if department:
            # Nối các phòng ban bằng NEWLINE để mỗi phòng ban xuống 1 dòng
            department_text = TextFormatEnum.NEWLINE.join(
                TextFormatEnum.DEPARTMENT_ITEM.format(department=dep) for dep in department
            )

            # Ghép chữ "Phòng ban:" với danh sách phòng ban ở dưới
            department_lines = f"{TextFormatEnum.DEPARTMENT_HEADER}{TextFormatEnum.NEWLINE}{department_text}"

            # Đưa toàn bộ block phòng ban xuống dưới content chính
            content = TextFormatEnum.NEWLINE.join([content, department_lines])

        # Build HTML text cho Task
        task_blocks = []
        lines = note.split('\n') if note else []

        formatted_lines = []
        for line in lines:
            cleaned_note = line.strip().lstrip('-').strip()
            if cleaned_note:
                note_line = f'{TextFormatEnum.TASK_PREFIX}{cleaned_note}'
                formatted_lines.append(note_line)

        output_text = '\n'.join(formatted_lines)
        note_line = output_text

        if tasks:
            for task in tasks:
                block = [
                    f"{TextFormatEnum.TASK_HEADER} {task.title} [{task.status}] {task.estimated_point}"
                ] if task.estimated_point else [
                    f"{TextFormatEnum.TASK_HEADER} {task.title} [{task.status}] {TextFormatEnum.SUBTASK_NOT_DONE} POINT"
                ]
                task_blocks.append(TextFormatEnum.NEWLINE.join(block))
            task_lines = TextFormatEnum.NEWLINE.join(task_blocks)
        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER} {TextFormatEnum.TASK_EMPTY}"

        first_line = f"[{TextFormatEnum.CHECKOUT_LATE}]" if checkout_late else f"[{TextFormatEnum.CHECKOUT_ON_TIME}]"
        if departure_status is not None:
            first_line = first_line + TextFormatEnum.TASK_PREFIX + f"[{DEPARTMENT_STATUS.get(departure_status)}]"
        if work_form:
            first_line = first_line + TextFormatEnum.TASK_PREFIX + f"[{work_form}]"

        # Ghép các dòng chính
        body_lines = [
            first_line,
            content,
            task_lines,
            TextFormatEnum.RESULT_NOTE,
            note_line,
        ]

        # Thêm dòng Đánh giá (in đậm) nếu có
        if evaluate:
            body_lines.append(TextFormatEnum.EVALUATE_HEADER)
            body_lines.append(TextFormatEnum.EVALUATE_VALUE.format(evaluate=evaluate))

        full_html_text = TextFormatEnum.NEWLINE.join(body_lines)

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
                                            "text": full_html_text
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

    @staticmethod
    def _get_bug_code(item_id: Any) -> str:
        """Hash ObjectId -> 6 ký tự hex unique, viết hoa."""
        return hashlib.md5(str(item_id).encode()).hexdigest()[:6].upper()

    @staticmethod
    def _format_field_value(field_key: str, value: Any) -> str:
        if value is None or value == "":
            return "(trống)"
        if field_key == "bug_type":
            return BUG_TYPE.get(value, str(value))
        if isinstance(value, list):
            return ", ".join(str(v) for v in value) if value else "(trống)"
        return str(value)

    @staticmethod
    def _bug_body_lines(item: "WorkItemResponse") -> list[str]:
        bug_type_label = BUG_TYPE.get(item.bug_type, item.bug_type or "")
        return [
            TextFormatEnum.BUG_META_LINE.format(bug_type=bug_type_label, screen=item.screen or ""),
            TextFormatEnum.BUG_EXTRA_INFO.format(extra_info=item.extra_info or ""),
            TextFormatEnum.BUG_DESCRIPTION.format(description=item.des or ""),
            TextFormatEnum.BUG_EXPECTED_RESULT.format(expected_result=item.explanation or ""),
        ]

    @staticmethod
    def build_bug_new_message(user_name: str, item: "WorkItemResponse") -> str:
        user_display = user_name or TextFormatEnum.GUEST
        bug_code = FormatContentGgChatAPI._get_bug_code(item.id)

        lines = [
            TextFormatEnum.BUG_NEW_HEADER,
            TextFormatEnum.BUG_CREATE_LINE.format(
                user=user_display, bug_code=bug_code, title=item.title or ""
            ),
            *FormatContentGgChatAPI._bug_body_lines(item),
        ]
        return TextFormatEnum.NEWLINE.join(lines)

    @staticmethod
    def build_bug_updated_message(
            user_name: str,
            item: "WorkItemResponse",
            changed_fields: Optional[dict[str, Any]] = None,
    ) -> str:
        user_display = user_name or TextFormatEnum.GUEST
        bug_code = FormatContentGgChatAPI._get_bug_code(item.id)

        lines = [
            TextFormatEnum.BUG_UPDATED_HEADER,
            TextFormatEnum.BUG_UPDATE_LINE.format(
                user=user_display, bug_code=bug_code, title=item.title or ""
            ),
            *FormatContentGgChatAPI._bug_body_lines(item),
        ]

        if changed_fields:
            lines.append("")  # dòng trống ngăn cách 2 block
            lines.append(TextFormatEnum.BUG_UPDATE_FIELDS_HEADER.format(user=user_display))
            for field_key, new_value in changed_fields.items():
                field_label = FIELD_LABEL_MAP.get(field_key, field_key)
                lines.append(
                    TextFormatEnum.BUG_UPDATE_FIELD_LINE.format(
                        field_label=field_label,
                        new_value=FormatContentGgChatAPI._format_field_value(field_key, new_value),
                    )
                )

        return TextFormatEnum.NEWLINE.join(lines)

    @staticmethod
    def build_bug_deleted_message(user_name: str, item: "WorkItemResponse") -> str:
        user_display = user_name or TextFormatEnum.GUEST
        bug_code = FormatContentGgChatAPI._get_bug_code(item.id)

        lines = [
            TextFormatEnum.BUG_DELETED_HEADER,
            TextFormatEnum.BUG_DELETE_LINE.format(
                user=user_display, bug_code=bug_code, title=item.title or ""
            ),
            *FormatContentGgChatAPI._bug_body_lines(item),
        ]
        return TextFormatEnum.NEWLINE.join(lines)

    @staticmethod
    def format_html_gg(content: str) -> dict:
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        return {
            "cardsV2": [
                {
                    "cardId": f"html_{now_vn.timestamp()}",
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