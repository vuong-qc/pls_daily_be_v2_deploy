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
    "AHEAD" : "VƯỢT TIẾN ĐỘ",
    "ON_TRACK" : "ĐANG ĐÚNG TIẾN ĐỘ ĐỀ RA",
    "BEHIND" : "CHẬM TIẾN ĐỘ ĐỀ RA",
    "UNFINISHED": "KHÔNG HOÀN THÀNH DEADLINE"
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
    "CONFIRMED": "Sẽ sửa"
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