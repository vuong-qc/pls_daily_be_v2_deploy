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
    CHECKIN_ON_TIME = "Check in đúng giờ"
    CHECKOUT_LATE = "Check out trễ"
    CHECKOUT_ON_TIME = "Check out đúng giờ"
    # ===== BUG NOTIFICATION =====
    BUG_NEW_HEADER = """⚠️ <font color="#CB1D21"><b>[BUG MỚI]</b></font>"""
    BUG_UPDATED_HEADER = """<font color="#F2994A"><b>[BUG ĐÃ CẬP NHẬT]</b></font>"""
    BUG_DELETED_HEADER = """<font color="#828282"><b>[BUG ĐÃ XÓA]</b></font>"""

    BUG_CREATOR = """&#8226; <b>Người tạo</b>: {user}"""
    BUG_UPDATER = """&#8226; <b>Người cập nhật</b>: {user}"""
    BUG_DELETER = """&#8226; <b>Người xóa</b>: {user}"""

    BUG_TITLE = """&#8226; <b>Bug</b>: {title}"""
    BUG_TYPE = """&#8226; <b>Loại</b>: {bug_type}"""
    BUG_SCREEN = """&#8226; <b>Màn hình</b>: {screen}"""
    BUG_EXTRA_INFO = """&#8226; <b>Thông tin</b>: {extra_info}"""
    GUEST = """🐣Người dùng ẩn danh🐣"""