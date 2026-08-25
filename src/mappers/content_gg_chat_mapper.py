ARRIVAL_STATUS = {
    "ARRIVE_LATE": '<font color="#FF0000"><b>ĐI LÀM TRỄ</b></font>',
    "ARRIVE_ON_TIME": '<font color="#2D9732"><b>Đến đúng giờ</b></font>',
    "LOGTIME_TIME": '<font color="#2D9732"><b>Giờ log time</b></font>',
}

DEPARTMENT_STATUS = {
    "LEAVE_EARLY": '<font color="#FF0000"><b>VỀ SỚM</b></font>',
    "LEAVE_ON_TIME": '<font color="#2D9732"><b>Về đúng giờ</b></font>',
    "OT": '<font color="#2D9732"><b>Làm thêm giờ, chạy task</b></font>',
    "LOGTIME_TIME": '<font color="#2D9732"><b>Giờ log time</b></font>',
}

EVALUATE_SESSION = {
    "AHEAD": '<font color="#2D9732"><b>VƯỢT TIẾN ĐỘ</b></font>',
    "ON_TRACK": '<font color="#2D9732"><b>ĐANG ĐÚNG TIẾN ĐỘ ĐỀ RA</b></font>',
    "BEHIND": '<font color="#FF0000"><b>CHẬM TIẾN ĐỘ ĐỀ RA</b></font>',
    "UNFINISHED": '<font color="#FF0000"><b>KHÔNG HOÀN THÀNH DEADLINE</b></font>',
}
WORK_FORM = {
    "WFH": '<font color="#FF0000"><b>WFH</b></font>',
    "IN_OFFICE" : """<font color="#2D9732"><b>IN OFFICE</b></font>"""
}

BUG_TYPE = {
    "BUG": "BUG",
    "FEEDBACK" : "Góp ý"
}
BUG_STATUS = {
    "NEW" : "Mới",
    "FIXING" : "Đang sửa",
    "VERIFIED" : "Xác nhận đã sửa",
    "FIXED" : "Đã sửa",
    "NO_HANDLE":  "Không xử lý",
    "LATER" : "Để sau",
    "DUPLICATE": "Trùng",
    "UNKNOWN": "Không xác định",
    "CONFIRMED": "Sẽ sửa",
    "NEW_FUNCTION" : "Function mới"
}

FIELD_LABEL_MAP: dict[str, str] = {
    "title": "Tên bug",
    "des": "Mô tả",
    "status": "Trạng thái",
    "priority": "Độ ưu tiên",
    "screen": "Màn hình",
    "bug_type": "Loại bug",
    "extra_info": "Thông tin thêm",
    "explanation": "Kết quả mong muốn",
    "deadline": "Deadline",
    "handler_id": "Người sửa",
    "assigned_id": "Người gây lỗi",
    "platform": "Nền tảng",
    "device": "Thiết bị",
    "device_version": "Phiên bản thiết bị",
    "project_version": "Phiên bản dự án",
    "action": "Hành động",
    "blame": "Nguyên nhân",
}
PRIORITY: dict[str, str] = {
    "HIGH" : "Ưu tiên cao",
    "FTF": "Critical",
    "LOW": "Ưu tiên thấp",
    "MEDIUM": "Ưu tiên trung bình",
    "NO_HANDLE" : "Không xử lý",
    "LATER": "Để sau",
    "DUPLICATE": "Trùng",
    "UNKNOWN": "Không xác định"
}