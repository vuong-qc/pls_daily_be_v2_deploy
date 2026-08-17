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

    DEPARTMENT_SEPARATOR = " &#8226; "
    # Chỉ bôi đậm chữ phòng ban, bỏ dấu bullet ở header
    DEPARTMENT_HEADER = "<b>Phòng ban</b>:"

    # Thêm dấu bullet (và một chút khoảng trắng lùi đầu dòng cho đẹp) vào trước tên phòng ban
    DEPARTMENT_ITEM = """&nbsp;&nbsp;&#8226; <font color="#197B32">{department}</font>"""

    EVALUATE_HEADER = """&#8226; <b>Đánh giá:</b>"""
    EVALUATE_VALUE = """<font color="#197B32"><b>{evaluate}</b></font>"""
    # ===== BUG NOTIFICATION =====
    BUG_NEW_HEADER = """⚠️ <b>[BUG MỚI]</b>"""
    BUG_UPDATED_HEADER = """<b>[BUG ĐÃ CẬP NHẬT]</b>"""
    BUG_DELETED_HEADER = """<b>[BUG ĐÃ XÓA]</b>"""
    BUG_CRITICAL = """[<font color=#dc3545><b>{priority}</b></font>] <font color=#dc3545><b>BUG</b></font>"""
    BUG_NORMAL = """<font color=#dc3545><b>BUG</b></font>"""
    BUG_FEEDBACK = "GÓP Ý"

    BUG_CREATE_LINE = """<font color="#CB1D21"><b>{user}</b></font> vừa tạo {bug} #{bug_code} - {title}"""
    BUG_UPDATE_LINE = """<font color="#F2994A"><b>{user}</b></font> vừa cập nhật {bug} #{bug_code} - {title}"""
    BUG_DELETE_LINE = """<font color="#828282"><b>{user}</b></font> vừa xóa bug #{bug_code} - {title}"""
    BUG_NEW = """<font color="#dc3545"><b>{status}</b></font>"""
    BUG_FIXING = """<font color="#fd7e14"><b>{status}</b></font>"""
    BUG_FIXED = """<font color="#0d6efd"><b>{status}</b></font>"""
    BUG_VERIFIED = """<font color="#198754"><b>{status}</b></font>"""

    BUG_TYPE_FEEDBACK = """<font color="#d97706"><b>{type}</b></font>"""
    BUG_TYPE_BUG = """<font color="#fd7e14"><b>{type}</b></font>"""
    BUG_TYPE_CRITICAL = """<font color="#dc3545"><b>{type}</b></font>"""

    BUG_SCREEN= """Màn hình: {screen}"""
    BUG_EXTRA_INFO = """Thông tin thêm: {extra_info}"""
    BUG_DESCRIPTION = """Mô tả: {description}"""
    BUG_EXPECTED_RESULT = """Kết quả mong muốn: {expected_result}"""

    BUG_UPDATE_FIELDS_HEADER = """<font color="#F2994A"><b>{user}</b></font> vừa cập nhật:"""
    BUG_UPDATE_FIELD_LINE = """&nbsp;&nbsp; {field_label} &rarr; {new_value}"""
    BUG_UPDATE_FIELD_LINE_BULLET = """&#8226; {field_label} : {new_value}"""  # dòng mới, chỉ dùng cho Người Sửa / Trạng Thái


    GUEST = """🐣Người dùng ẩn danh🐣"""
    USERNAME = """<font color=#dc3545><b>{username}</b></font>"""
    BOLD = """<b>{username}</b>"""
    OWNER = """của <font color=#0d6efd><b>{username}</b></font>"""
