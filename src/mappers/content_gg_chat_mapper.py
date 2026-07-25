ARRIVAL_STATUS = {
    "ARRIVE_LATE" : "Đến trễ",
    "ARRIVE_ON_TIME": "Đến đúng giờ",
    "LOGTIME_TIME": "Giờ log time"
}

DEPARTMENT_STATUS = {
    "LEAVE_EARLY" : "Về sớm",
    "LEAVE_ON_TIME" : "Về đúng giờ",
    "OT": "Làm thêm giờ, chạy task",
    "LOGTIME_TIME": "Giờ log time"
}

EVALUATE_SESSION = {
    "AHEAD" : "Vượt tiến độ",
    "ON_TRACK" : "Đang đúng tiến độ đề ra",
    "BEHIND" : "Chậm tiến độ được giao",
    "UNFINISHED": "Không hoàn thành deadline"
}

BUG_TYPE = {
    "BUG": "BUG",
    "FEEDBACK" : "Góp ý"
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
    "handler_id": "Người xử lý",
    "assigned_id": "Người được giao",
    "platform": "Nền tảng",
    "device": "Thiết bị",
    "device_version": "Phiên bản thiết bị",
    "project_version": "Phiên bản dự án",
    "action": "Hành động",
    "blame": "Nguyên nhân",
}