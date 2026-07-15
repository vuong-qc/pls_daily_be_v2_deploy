from enum import StrEnum

class TextFormatEnum(StrEnum):
    # Dùng thẻ <font> và <b> thoải mái vì chúng ta sẽ đưa nó vào Card
    CHECKIN = """<b>{time}</b>, <font color="#CB1D21"><b>{user}</b></font> checked in!"""
    CHECKIN_DEPART = """<b>{time}</b>, <font color="#CB1D21"><b>{user}</b></font> {department} checked in!"""
    TASK_HEADER = "&#8226; <b>Task</b>:"
    SUBTASK_HEADER = "&#8226; <b>Subtask</b>:"
    TASK_PREFIX = "&nbsp;&nbsp;- " # Dùng &nbsp; để lùi đầu dòng trong HTML
    REMIND_CHECK_IN = "Hãy checkin đi người đẹp <font color=\"#CB1D21\"><b>{user}</b></font> ơi! ~~~~~~~"
    REMIND_CHECK_OUT = "Người đẹp <font color=\"#CB1D21\"><b>{user}</b></font> ơi nhớ check out rùi mới về với gia đình, để dành sức cho ngày mai bán mình!!!"
    TASK_EMPTY = "Không chọn task"
    NOTE = '&#8226; <b>Ghi chú</b>:'
    NEWLINE = '<br>' # Xuống dòng trong HTML
    SPACE = ' '
    RESULT_NOTE = "&#8226; <b>Ghi chú kết quả</b>:"
    CHECKOUT = """<b>{time}</b>, <font color="#CB1D21"><b>{user}</b></font> checked out!"""
    CHECKOUT_DEPART = """<b>{time}</b>, <font color="#CB1D21"><b>{user}</b></font> {department} checked out!"""
    SUBTASK_EMPTY = "Không tạo subtask"
    SUBTASK_NOT_DONE = "Chưa hoàn thành subtask"
    CHECKIN_LATE = "Check in trễ"
    CHECKOUT_LATE = "Check out trễ"