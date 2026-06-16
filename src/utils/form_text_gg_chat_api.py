from datetime import datetime
from src.enums.text_format_enum import TextFormatEnum
from src.configs import settings
from zoneinfo import ZoneInfo

class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name:str, tasks: list[str], note:str):
        tz_vn = ZoneInfo(settings.TZ)
        now_vn = datetime.now(tz_vn)
        content = TextFormatEnum.CHECKIN.format(time=now_vn.strftime("%Y-%m-%d %H:%M:%S"), user=user_name)

        task_lines = '\n'.join(
            f'\t{TextFormatEnum.TASK_PREFIX}{task}'
            for task in tasks
        ) if tasks else ''.join(
            [f'{TextFormatEnum.SPACE}{TextFormatEnum.TASK_EMPTY}']
        )
        task_lines = TextFormatEnum.TASK_HEADER + TextFormatEnum.NEWLINE + task_lines if tasks else  TextFormatEnum.TASK_HEADER + task_lines
        note_line = '\n'.join(
            [f'\t{TextFormatEnum.TASK_PREFIX}{note}']
        )
        return '\n'.join([
            content,
            task_lines,
            TextFormatEnum.NOTE,
            note_line
        ])
    @staticmethod
    def format_content_remind_checkin(user_name):
        content = TextFormatEnum.REMIND_CHECK_IN.format(user=user_name)
        return content
    @staticmethod
    def format_content_remind_checkout(user_name):
        content = TextFormatEnum.REMIND_CHECK_OUT.format(user=user_name)
        return content
