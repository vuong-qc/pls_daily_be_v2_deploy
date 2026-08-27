from datetime import datetime
from typing import Optional, Any
from zoneinfo import ZoneInfo
from src.configs import settings
from src.enums.text_format_enum import TextFormatEnum
from src.models.task.response.task_response_model import TaskResponse
from src.models.work_item.response.work_item_response_model import WorkItemResponse
from src.mappers.content_gg_chat_mapper import (ARRIVAL_STATUS, DEPARTMENT_STATUS, BUG_TYPE,
                                                FIELD_LABEL_MAP, EVALUATE_SESSION, BUG_STATUS,
                                                PRIORITY, WORK_FORM)
from src.enums.bug_status_enum import BugStatusEnum
from src.enums.bug_type_enum import BugTypeEnum
from src.enums.task_priority_enum import TaskPriorityEnum
from src.enums.session_status_enum import ArrivalStatusEnum, DepartmentStatusEnum, WorkFormEnum
import hashlib

import json
import re


def extract_plain_text_from_delta(delta_raw) -> str:
    """
    delta_raw có thể là:
    - chuỗi JSON: '[{"insert":"..."}]'
    - hoặc dict: {"ops": [...]}
    - hoặc list: [{"insert": "..."}]
    """
    try:
        ops = json.loads(delta_raw, strict=False) if isinstance(delta_raw, str) else delta_raw
    except (json.JSONDecodeError, TypeError):
        return str(delta_raw)  # fallback: không parse được thì trả nguyên text

    if isinstance(ops, dict):
        ops = ops.get("ops", [])
    if not isinstance(ops, list):
        return ""

    text_parts = []
    for op in ops:
        insert = op.get("insert") if isinstance(op, dict) else None
        if isinstance(insert, str):
            text_parts.append(insert)
        # insert là dict (image/video/embed) -> bỏ qua

    return "".join(text_parts)


def is_junk_text(text: str, max_len: int = 200) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if re.search(r'(.)\1{19,}', stripped):   # 1 ký tự lặp liên tục >=20 lần
        return True
    if len(stripped) > max_len and ' ' not in stripped:  # dài mà không có space
        return True
    return False

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
        if nickname and nickname.strip():
            user_name = f"{user_name} ({nickname.strip()})"

        # Build department text: mỗi phòng ban tô xanh lá, nối bằng dấu •


        content = TextFormatEnum.CHECKIN.format(
                time=now_vn.strftime("%d.%m.%Y %H:%M"), user=user_name, checkin_time=now_vn.strftime("%-I:%M %p"),
            )

        if department:
            # Nối các phòng ban bằng NEWLINE để mỗi phòng ban xuống 1 dòng
            department_text = ", ".join(
                dep
                for dep in department
            )

            # Ghép chữ "Phòng ban:" với danh sách phòng ban ở dưới
            department_lines = f"{TextFormatEnum.DEPARTMENT_HEADER}{TextFormatEnum.NEWLINE}{TextFormatEnum.DEPARTMENT_ITEM.format(department=department_text)}"

            # Đưa toàn bộ block phòng ban xuống dưới content chính
            content = TextFormatEnum.NEWLINE.join([content, department_lines])
        first_line = ""
        if checkin_late:
            first_line = f"[{TextFormatEnum.CHECKIN_LATE}]"

        if arrival_status is not None:
            if first_line and arrival_status == ArrivalStatusEnum.ARRIVE_LATE:
                first_line = first_line + TextFormatEnum.TASK_PREFIX+ f"[{ARRIVAL_STATUS.get(arrival_status)}]"
            elif arrival_status == ArrivalStatusEnum.ARRIVE_LATE:
                first_line = f"[{ARRIVAL_STATUS.get(arrival_status)}]"
        if work_form is not None:
            if first_line and work_form == WorkFormEnum.WFH:
                first_line = first_line + TextFormatEnum.TASK_PREFIX + f"[{WORK_FORM.get(work_form)}]"
            elif work_form == WorkFormEnum.WFH:
                first_line = f"[{WORK_FORM.get(work_form)}]"
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
            item for item in [first_line,
            content,
            task_lines,
            TextFormatEnum.NOTE,
            note_line]
            if item
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
                                evaluate: Optional[str] = None, start_time: Optional[datetime] = None,
                                ) -> dict:
        tz_vn = ZoneInfo(settings.TZ)

        # =========================
        # Format end time
        # =========================
        now_vn = datetime.now(tz_vn)

        if end_time and end_time.tzinfo is None:
            now_vn = end_time.replace(tzinfo=tz_vn)
        elif end_time:
            now_vn = end_time.astimezone(tz_vn)

        # =========================
        # Format username
        # =========================
        if nickname and nickname.strip():
            user_name = f"{user_name} ({nickname.strip()})"

        # =========================
        # Format start time
        # =========================
        start_vn = None

        if start_time:
            if start_time.tzinfo is None:
                start_vn = start_time.replace(tzinfo=tz_vn)
            else:
                start_vn = start_time.astimezone(tz_vn)

        # =========================
        # Calculate working time
        # =========================
        work_time = ""
        duration = ""

        if start_vn:
            # Ví dụ: 9h00 - 18h30
            start_str = f"{start_vn.hour}h{start_vn.minute:02d}"
            end_str = f"{now_vn.hour}h{now_vn.minute:02d}"

            work_time = f"{start_str} - {end_str}"

            # Tổng thời gian làm việc
            total_minutes = int(
                (now_vn - start_vn).total_seconds() // 60
            )

            hours = total_minutes // 60
            minutes = total_minutes % 60

            if hours and minutes:
                duration = f"{hours} giờ {minutes} phút"
            elif hours:
                duration = f"{hours} giờ"
            else:
                duration = f"{minutes} phút"

        # =========================
        # Build checkout content
        # =========================
        content = TextFormatEnum.CHECKOUT.format(
            time=now_vn.strftime("%d.%m.%Y %H:%M"),
            user=user_name,
            work_time=work_time,
            duration=duration,
        )

        if department:
            # Nối các phòng ban bằng NEWLINE để mỗi phòng ban xuống 1 dòng
            department_text = ", ".join(
                dep
                for dep in department
            )

            # Ghép chữ "Phòng ban:" với danh sách phòng ban ở dưới
            department_lines = f"{TextFormatEnum.DEPARTMENT_HEADER}{TextFormatEnum.NEWLINE}{TextFormatEnum.DEPARTMENT_ITEM.format(department=department_text)}"

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
                    f"{TextFormatEnum.TASK_HEADER} {task.title} [{task.status}] {task.estimated_point} POINT"
                ] if task.estimated_point else [
                    f"{TextFormatEnum.TASK_HEADER} {task.title} [{task.status}] {TextFormatEnum.SUBTASK_NOT_DONE}"
                ]
                task_blocks.append(TextFormatEnum.NEWLINE.join(block))
            task_lines = TextFormatEnum.NEWLINE.join(task_blocks)
        else:
            task_lines = f"{TextFormatEnum.TASK_HEADER} {TextFormatEnum.TASK_EMPTY}"

        first_line = f"[{TextFormatEnum.CHECKOUT_LATE}]" if checkout_late else ""
        if departure_status is not None:
            if first_line and (departure_status == DepartmentStatusEnum.LEAVE_EARLY or departure_status == DepartmentStatusEnum.OT):
                first_line = first_line + TextFormatEnum.TASK_PREFIX + f"[{DEPARTMENT_STATUS.get(departure_status)}]"
            elif departure_status == DepartmentStatusEnum.LEAVE_EARLY or departure_status == DepartmentStatusEnum.OT:
                first_line = f"[{DEPARTMENT_STATUS.get(departure_status)}]"

        if work_form is not None:
            if first_line and work_form == WorkFormEnum.WFH:
                first_line = first_line + TextFormatEnum.TASK_PREFIX + f"[{WORK_FORM.get(work_form)}]"
            elif work_form == WorkFormEnum.WFH:
                first_line = f"[{WORK_FORM.get(work_form)}]"
        # Thêm dòng Đánh giá (in đậm) nếu có
        if evaluate:
            department_lines = f"{TextFormatEnum.EVALUATE_VALUE.format(evaluate=EVALUATE_SESSION[evaluate])}"

            note_line = TextFormatEnum.NEWLINE.join(
                [note_line, department_lines]
            )

        # Ghép các dòng chính
        body_lines = [
            item for item in[first_line,
            content,
            task_lines,
            TextFormatEnum.RESULT_NOTE,
            note_line]
            if item
        ]


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
    def _format_field_value(field_key: str, value: Any, root_data: "WorkItemResponse") -> str:
        print("field_key:", field_key)
        print("value:", value)
        print("root_data:", root_data)
        if value is None or value == "":
            return "(trống)"
        if field_key == "bug_type":
            # Lấy tên hiển thị của bug type (ví dụ: "Feedback", "Bug"...)
            type_label = BUG_TYPE.get(value, str(value))

            # 1. Dạng Feedback -> Màu vàng
            if value == BugTypeEnum.BUG_TYPE_FEEDBACK:
                return TextFormatEnum.BUG_TYPE_FEEDBACK.format(type=type_label)

            # 2. Dạng Bug + Priority FTF -> Coi như Critical -> Màu đỏ
            elif value == BugTypeEnum.BUG_TYPE_BUG and root_data.priority and root_data.priority == TaskPriorityEnum.FTF:
                return TextFormatEnum.BUG_TYPE_CRITICAL.format(type=type_label)

            # 3. Dạng Bug bình thường -> Màu cam
            elif value == BugTypeEnum.BUG_TYPE_BUG:
                return TextFormatEnum.BUG_TYPE_BUG.format(type=type_label)

            # Fallback mặc định nếu không khớp điều kiện nào ở trên
            return type_label
        if field_key == "handler_id":
            return (
                ", ".join(TextFormatEnum.USERNAME.format(username=v.name) for v in root_data.handler)
                if root_data.handler else "(trống)"
            )

        if field_key == "assigned_id":
            return (
                ", ".join(TextFormatEnum.USERNAME.format(username=v.name) for v in root_data.assignee)
                if root_data.assignee else "(trống)"
            )
        if isinstance(value, list):
            return ", ".join(str(v) for v in value) if value else "(trống)"
        if field_key == "status":
            status= BUG_STATUS.get(value, str(value))
            if value == BugStatusEnum.NEW:
                return TextFormatEnum.BUG_NEW.format(status=status)
            if value == BugStatusEnum.FIXED:
                return TextFormatEnum.BUG_FIXED.format(status=status)
            if value == BugStatusEnum.FIXING:
                print("status:", TextFormatEnum.BUG_FIXING.format(status=status))
                return TextFormatEnum.BUG_FIXING.format(status=status)
            if value == BugStatusEnum.VERIFIED:
                return TextFormatEnum.BUG_VERIFIED.format(status=status)
            return TextFormatEnum.BOLD.format(username=BUG_STATUS.get(value, str(value)))

        if field_key == "priority":
            return PRIORITY.get(value, str(value))

        if field_key == "screen":
            return TextFormatEnum.BUG_SCREEN.format(screen=value)
        if field_key == "extra_info":
            return TextFormatEnum.BUG_EXTRA_INFO.format(extra_info=value)
        if field_key == "des":
            plain_text = extract_plain_text_from_delta(value).strip()
            return TextFormatEnum.BUG_DESCRIPTION.format(description=plain_text)
        if field_key == "explanation":
            return TextFormatEnum.BUG_EXPECTED_RESULT.format(expected_result= value)
        if field_key == "note":
            plain_text = extract_plain_text_from_delta(value).strip()
            return plain_text
        return str(value)
    @staticmethod
    def _format_title(root_data: WorkItemResponse, name:str) -> str:
        value = root_data.bug_type
        # 1. Dạng Feedback -> Màu vàng
        if value == BugTypeEnum.BUG_TYPE_FEEDBACK:
            return TextFormatEnum.BUG_TYPE_FEEDBACK.format(type=name)

        # 2. Dạng Bug + Priority FTF -> Coi như Critical -> Màu đỏ
        elif value == BugTypeEnum.BUG_TYPE_BUG and root_data.priority and root_data.priority == TaskPriorityEnum.FTF:
            return TextFormatEnum.BUG_TYPE_CRITICAL.format(type=name)

        # 3. Dạng Bug bình thường -> Màu cam
        elif value == BugTypeEnum.BUG_TYPE_BUG:
            return TextFormatEnum.BUG_TYPE_BUG.format(type=name)

        # Fallback mặc định nếu không khớp điều kiện nào ở trên
        return name
    @staticmethod
    def _format_bug_type(root_data: WorkItemResponse) -> str:
        if root_data.bug_type == BugTypeEnum.BUG_TYPE_FEEDBACK:
            return TextFormatEnum.BUG_TYPE_FEEDBACK.format(type=TextFormatEnum.BUG_FEEDBACK)
        else:
            if root_data.priority and root_data.priority == TaskPriorityEnum.FTF:
                return TextFormatEnum.BUG_CRITICAL.format(priority=PRIORITY[root_data.priority])
            return TextFormatEnum.BUG_NORMAL

    @staticmethod
    def _bug_body_lines(item: "WorkItemResponse") -> list[str]:
        bug_type_label = BUG_TYPE.get(item.bug_type, item.bug_type or "")
        res = []
        if item.screen:
            res.append(TextFormatEnum.BUG_SCREEN.format(screen=item.screen))
        if item.extra_info:
            res.append(TextFormatEnum.BUG_EXTRA_INFO.format(extra_info=item.extra_info))
        if item.des:
            plain_text = extract_plain_text_from_delta(item.des).strip()
            if not is_junk_text(plain_text):
                res.append(TextFormatEnum.BUG_DESCRIPTION.format(description=plain_text))
        if item.explanation:
            res.append(TextFormatEnum.BUG_EXPECTED_RESULT.format(expected_result=item.explanation))
        return res

    @staticmethod
    def build_bug_new_message(user_name: str, item: "WorkItemResponse") -> str:
        user_display = TextFormatEnum.BOLD.format(username= user_name)  or TextFormatEnum.GUEST
        bug_code = FormatContentGgChatAPI._get_bug_code(item.id)
        bug_type = FormatContentGgChatAPI._format_bug_type(item)
        lines = [
            # TextFormatEnum.BUG_NEW_HEADER,
            TextFormatEnum.BUG_CREATE_LINE.format(
                user=user_display, bug_code=bug_code, title= FormatContentGgChatAPI._format_title(item, item.title), bug = bug_type
            ),
            # *FormatContentGgChatAPI._bug_body_lines(item),
        ]
        return TextFormatEnum.NEWLINE.join(lines)

    @staticmethod
    def build_bug_updated_message(
            user_name: str,
            item: "WorkItemResponse",
            old_item: "WorkItemResponse",
            changed_fields: Optional[dict[str, Any]] = None,
    ) -> str:
        user_display = TextFormatEnum.BOLD.format(username= user_name) or TextFormatEnum.GUEST
        bug_code = FormatContentGgChatAPI._get_bug_code(item.id)
        owner = item.owner
        bug_type = FormatContentGgChatAPI._format_bug_type(item)
        update_line = TextFormatEnum.BUG_UPDATE_LINE.format(
                user=user_display, bug_code=bug_code, title= FormatContentGgChatAPI._format_title(item, item.title), bug=bug_type
            )
        if owner:
            update_line = update_line + TextFormatEnum.SPACE+ TextFormatEnum.OWNER.format(username=owner.name)

        lines = [
            # TextFormatEnum.BUG_UPDATED_HEADER,
            update_line,
            # *FormatContentGgChatAPI._bug_body_lines(item),

        ]

        if changed_fields:
            lines.append("")  # dòng trống ngăn cách 2 block

            lines.append(
                TextFormatEnum.BUG_UPDATE_FIELD_LINE_BULLET.format(
                    field_label=FIELD_LABEL_MAP["handler_id"],
                    new_value=FormatContentGgChatAPI._format_field_value("handler_id", old_item.handler_id, old_item),
                )
            )
            lines.append(
                TextFormatEnum.BUG_UPDATE_FIELD_LINE_BULLET.format(
                    field_label=FIELD_LABEL_MAP["status"],
                    new_value=FormatContentGgChatAPI._format_field_value("status", old_item.status, old_item),
                )
            )
            lines.append(
                ""
            )

            for field_key, new_value in changed_fields.items():
                field_label = FIELD_LABEL_MAP.get(field_key, field_key)
                lines.append(
                    TextFormatEnum.BUG_UPDATE_FIELD_LINE.format(
                        field_label=TextFormatEnum.BOLD.format(username=field_label),
                        new_value=FormatContentGgChatAPI._format_field_value(field_key, new_value, item),
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