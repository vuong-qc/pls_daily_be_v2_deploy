from typing import List
from beanie import View
from pydantic import BaseModel
from src.configs import settings
from src.models.session.session_document import SessionDocument
from src.models.user.user_document import UserDocument
from beanie import PydanticObjectId
from datetime import datetime
from typing import Optional
from src.models.user.response.user_response_model import UserResponse

# Bạn có thể tự custom các fields bạn cần trả về để tối ưu hiệu năng
class SessionInGroup(BaseModel):
    id: PydanticObjectId
    user_id: str
    status: str
    notes: str
    list_task: List[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    user_info: Optional[UserResponse] = None

class DailySessionView(View):
    id: str  # Trong View, id này chính là chuỗi ngày YYYY-MM-DD từ $group
    user_id: str # Thêm field này ở tầng group để tiện filter sau này
    total_sessions: int
    sessions: List[SessionInGroup]

    class Settings:
        source = SessionDocument
        name = "daily_sessions_view"
        pipeline = [
            # Bước 1: Join với collection User
            {
                "$lookup": {
                    "from": "users",  # Hãy chắc chắn tên collection trong DB trùng với chuỗi này
                    "localField": "user.$id",  # Đường dẫn DBRef của Beanie
                    "foreignField": "_id",
                    "as": "user_info_array"
                }
            },
            {
                "$match": {
                    "user_info_array": {"$ne": []}
                }
            },
            # Bước 2: Bóc mảng user_info_array thành 1 Object đơn lẻ
            {
                "$addFields": {
                    "user_info": {"$arrayElemAt": ["$user_info_array", 0]}
                }
            },
            # Bước 3: Đổi tên trường _id thành id cho User để Pydantic đọc hiểu được
            {
                "$addFields": {
                    "user_info.id": "$user_info._id"
                }
            },
            # Bước 4: Group theo ngày (local timezone) và user_id
            {
                "$group": {
                    "_id": {
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$start_time",
                                "timezone": settings.TZ
                            }
                        },
                        "user_id": "$user_id"
                    },
                    "sessions": {
                        "$push": {
                            "id": "$_id",
                            "user_id": "$user_id",
                            "status": "$status",
                            "notes": "$notes",
                            "list_task": "$list_task",
                            "start_time": "$start_time",
                            "end_time": "$end_time",
                            "user_info": "$user_info"  # Đã có sẵn tất cả các trường từ UserResponse nhờ $addFields
                        }
                    },
                    "total_sessions": {"$sum": 1}
                }
            },
            # Bước 5: Định hình cấu trúc phẳng (Flat) cho View
            {
                "$project": {
                    "_id": 0,
                    "id": "$_id.date",
                    "user_id": "$_id.user_id",
                    "total_sessions": 1,
                    "sessions": 1
                }
            }
        ]