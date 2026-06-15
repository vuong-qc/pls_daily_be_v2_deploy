from datetime import datetime
from src.enums.text_format_enum import TextFormatEnum
class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name:str, tasks: list[str]):
        content = TextFormatEnum.CHECKIN.format(time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user=user_name)

        task_lines = '\n'.join(
            f'{TextFormatEnum.TASK_PREFIX}{task}'
            for task in tasks
        )

        return '\n'.join([
            content,
            TextFormatEnum.TASK_HEADER,
            task_lines,
        ])
    @staticmethod
    def format_content_remind_checkin(user_name):
        content = TextFormatEnum.REMIND_CHECK_IN.format(user=user_name)
        return content
    @staticmethod
    def format_content_remind_checkout(user_name):
        content = TextFormatEnum.REMIND_CHECK_OUT.format(user=user_name)
        return content
