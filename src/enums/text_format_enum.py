from enum import StrEnum

class TextFormatEnum(StrEnum):
    # Dùng thẻ <font> và <b> thoải mái vì chúng ta sẽ đưa nó vào Card
    CHECKIN = """<b>{time}</b>, <font color="#CB1D21"><b>{user}</b></font> checked in!"""
    TASK_HEADER = "- <b>Task</b>:"
    TASK_PREFIX = "&nbsp;&nbsp;- " # Dùng &nbsp; để lùi đầu dòng trong HTML
    REMIND_CHECK_IN = "Hãy chekin đi người đẹp <font color=\"#CB1D21\"><b>{user}</b></font> ơi! ~~~~~~~"
    REMIND_CHECK_OUT = "Người đẹp <font color=\"#CB1D21\"><b>{user}</b></font> ơi nhớ check out rùi mới về với gia đình, để dành sức cho ngày mai bán mình!!!"
    TASK_EMPTY = "Không chọn task"
    NOTE = '- <b>Ghi chú</b>:'
    NEWLINE = '<br>' # Xuống dòng trong HTML
    SPACE = ' '