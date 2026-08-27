from src.repositories.notification.notification_repository import NotificationRepository
from src.models.notification.notification_document import NotificationDocument
from src.models.notification.request.filter_notification_model import FilterNotificationModel
from beanie.operators import Set, In, RegEx, GTE ,LT, NotIn, Or, Eq
import re
from beanie import UpdateResponse, PydanticObjectId
from src.utils.datetime_util import DateTimeUtil

class BeanieNotificationRepository(NotificationRepository):
    async def create_noti(self, data: dict):
        notification = NotificationDocument(**data)
        return await notification.insert()
    async def update_noti(self, noti_id:str, data: dict):
        notification = await NotificationDocument.get(noti_id)
        if notification:
            return await notification.update(Set(data))
        return None
    async def delete_noti(self, noti_id: str):
        notification = await NotificationDocument.get(noti_id)
        if notification:
            return await notification.delete()
        return None
    async def get_noti(self, noti_id: str):
        notification = await NotificationDocument.get(noti_id)
        return notification

    async def get_list_noti(self, filters: FilterNotificationModel) -> tuple[list[NotificationDocument], int]:
        filter_dump = filters.model_dump(exclude_unset=True)
        offset = filter_dump.pop("offset", 0)
        limit = filter_dump.pop("limit", 10)

        is_random = filter_dump.pop("is_random", False)
        is_expired = filter_dump.pop("is_expired", None)

        if filters.viewer_ids:
            filter_dump.update(
                NotIn(NotificationDocument.viewer_ids, filter_dump.pop("viewer_ids"))
            )
        if filters.departments:
            filter_dump.update(
                Or(
                    In(NotificationDocument.departments, filter_dump.pop("departments")),
                    Eq(NotificationDocument.departments, [])
                )
            )

        if filters.search:
            keyword = filter_dump.pop("search").strip().split()
            normalized = " ".join(keyword)
            escaped = re.escape(normalized)
            regex = f".*{escaped}.*"
            filter_dump.update(
                Or(
                    RegEx(NotificationDocument.title, regex, "i"),
                    RegEx(NotificationDocument.description, regex, "i"),
                )
            )
        ex_act_op = filter_dump.pop("expired_or_active", None)

        if is_expired:
            if ex_act_op:
                is_active = filter_dump.pop("is_active", None)
                if is_active is not None:
                    filter_dump.update(
                        Or(
                            LT(NotificationDocument.end_time, DateTimeUtil.current_milli_time()),
                            Eq(NotificationDocument.is_active, is_active)
                        )
                    )
            else:
                filter_dump.update(
                    LT(NotificationDocument.end_time, DateTimeUtil.current_milli_time())
                )
        else:
            if is_expired is None:
                pass
            else:
                if ex_act_op:
                    is_active = filter_dump.pop("is_active", None)
                    if is_active is not None:
                        filter_dump.update(
                            Or(
                                GTE(NotificationDocument.end_time, DateTimeUtil.current_milli_time()),
                                Eq(NotificationDocument.is_active, is_active)
                            )
                        )
                else:
                    filter_dump.update(
                            GTE(NotificationDocument.end_time, DateTimeUtil.current_milli_time())
                    )

        query = NotificationDocument.find(filter_dump)
        print("filter", filter_dump)
        count = await query.count()

        if is_random:
            items = await NotificationDocument.find(filter_dump).aggregate(
                [{"$sample": {"size": limit}}],
                projection_model=NotificationDocument
            ).to_list()
        else:
            items = await query.sort(f"+{NotificationDocument.updated_at}").skip(offset).limit(limit).to_list()
        return items, count
    async def add_viewer_noti(self, noti_id:str, user_id: str):
        pipeline_set = {

            # Logic cập nhật update_user bằng DB
            "viewer_ids": {
                "$concatArrays": [
                    {
                        "$filter": {
                            # Nếu field chưa có (null), mặc định là mảng rỗng []
                            "input": {"$ifNull": ["$viewer_ids", []]},
                            "as": "user",
                            # Lọc bỏ phần tử bị trùng với update_user truyền vào
                            "cond": {"$ne": ["$$user", user_id]}
                        }
                    },
                    # Nối thêm user_id vào cuối
                    [user_id]
                ]
            }
        }

        # 2. Thực thi lệnh update ngay trên DB (Truyền dưới dạng list để kích hoạt Pipeline Update)
        # Trả về document sau khi update
        noti = await NotificationDocument.find_one({"_id": PydanticObjectId(noti_id)}).update(
            [{"$set": pipeline_set}],
            response_type=UpdateResponse.NEW_DOCUMENT  # Để hàm trả về docs mới nhất
        )
        return noti