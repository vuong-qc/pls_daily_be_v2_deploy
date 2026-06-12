from datetime import datetime
class FormatContentGgChatAPI:
    @staticmethod
    def format_content_checkin(user_name:str, tasks: list[str]):
        content = f'{datetime.now()}, {user_name} checked in!'
        content+= f'\n Task :'
        for task in tasks:
            content += f'\n - {task}'

        return content