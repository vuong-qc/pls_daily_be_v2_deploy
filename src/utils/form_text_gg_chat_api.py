from datetime import datetime
from src.enums.text_format_enum import TextFormatEnum
class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name:str, tasks: list[str]):
        content = TextFormatEnum.CHECKIN.format(time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_name=user_name)

        task_lines = '\n'.join(
            f'{TextFormatEnum.TASK_PREFIX}{task}'
            for task in tasks
        )

        return '\n'.join([
            content,
            TextFormatEnum.TASK_HEADER,
            task_lines,
        ])