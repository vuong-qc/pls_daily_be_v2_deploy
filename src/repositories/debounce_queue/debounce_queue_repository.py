import json
import time
from typing import AsyncIterable

import redis.asyncio as aioredis

from src.configs import settings

DUE_SET = "debounce:due" # sorted set : {key: time send}
DEBOUNCE_SECONDS = 600
MAX_WAIT_SECONDS = 600
DATA_TTL_SECONDS =  MAX_WAIT_SECONDS * 3

# Mỗi nhóm thông báo (key, vd "bug_update:<bug_id>:<handler_id>") dùng 4 thứ trong Redis:
#   debounce:due               Sorted Set  danh sách "nhóm nào, gửi lúc nào" (sắp theo giờ gửi)
#   debounce:entries:{key}     List        mỗi lần sửa 1 dòng JSON, giữ đúng thứ tự, KHÔNG khử trùng
#   debounce:meta:{key}        String      JSON thông tin hiển thị mới nhất (tên handler, candidate, job)
#   debounce:first:{key}       String      thời điểm sửa đầu tiên, để tính trần MAX_WAIT

class DebounceQueueRepository:
    def __init__(self):
        self.redis = aioredis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT,
            decode_responses=True # return str instead bytes
        )

    async def push(self, key: str, entry: dict, meta: dict):
        now = time.time()
        first_key = f"debounce:first:{key}"
        entries_key = f"debounce:entries:{key}"
        meta_key = f"debounce:meta:{key}"

        # set key value NX EX ttl
        # NX = write when not exist -> keep at first modify
        # EX = auto delete after ttl s
        await self.redis.set(first_key, now, nx=True, ex=DATA_TTL_SECONDS)
        # get key: read value again (of first, or
        first_at = float(await self.redis.get(first_key) or now)
        send_at = min(now + DEBOUNCE_SECONDS, first_at + MAX_WAIT_SECONDS)

        # pipeline(transaction=True) = MULTI/EXEC: các lệnh bên trong chạy liền nhau như 1 khối,
        # không ai chen vào giữa, và chỉ tốn 1 lần gọi mạng. Nhờ vậy không có chuyện
        # "đã ghi entry nhưng chưa kịp hẹn giờ gửi" nếu process chết giữa chừng.

        async with self.redis.pipeline(transaction=True) as pipe:
            # rpush list value: add to last (create if not exist)
            # no overwrite, modify same field
            pipe.rpush(entries_key, json.dumps(entry, default=str))
            # set: overwrite mete by newest info
            pipe.set(meta_key, json.dumps(meta, default=str))
            # expire key ttl: set ttl for key (renew every time push)
            pipe.expire(entries_key, DATA_TTL_SECONDS)
            pipe.expire(meta_key, DATA_TTL_SECONDS)
            # zadd set {member: score}: add member with score, if memer exist, overwrite score
            pipe.zadd(DUE_SET, {key: send_at})
            await pipe.execute()

    async def pop_due(self)-> AsyncIterable[tuple[dict, list[dict]]]:
        """Lần lượt trả về (meta, entries) của từng nhóm đã đến giờ gửi; mỗi nhóm bị xoá khỏi Redis khi được lấy ra.

                Lấy từng nhóm một (không gom cả lô) để nếu lúc gửi nhóm này bị lỗi/timeout thì
                các nhóm sau vẫn còn nguyên trong Redis, chỉ có nhóm đang xử lý là có thể mất.
                """
        while True:
            # ZRANGEBYSCORE set min max LIMIT 0 1: lấy 1 member có score trong [min, max]
            # -> tức là 1 nhóm có giờ gửi <= bây giờ
            keys = await self.redis.zrangebyscore(DUE_SET, 0, time.time(), start=0, num=1)
            if not keys:
                return
            key = keys[0]

            # ZREM set member: xoá member, trả về số member đã xoá (1 hoặc 0).
            # Nhiều worker cùng lấy 1 nhóm thì chỉ 1 người nhận 1, người khác nhận 0 -> không gửi trùng
            if await self.redis.zrem(DUE_SET, key) != 1:
                continue

            entries_key = f"debounce:entries:{key}"
            meta_key = f"debounce:meta:{key}"
            # Đọc + xoá trong cùng 1 transaction: lần sửa chen vào sau đó sẽ thành 1 nhóm mới, không bị mất
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.lrange(entries_key, 0, -1)  # LRANGE: đọc toàn bộ list (0 .. -1 = đến cuối)
                pipe.get(meta_key)  # GET: đọc meta
                pipe.delete(entries_key, meta_key, f"debounce:first:{key}")  # DEL: xoá các key của nhóm
                entries, meta, _ = await pipe.execute()

            if not entries or not meta:
                # xảy ra khi tên nhóm còn trong DUE_SET nhưng dữ liệu đã hết hạn / đã được lần flush trước gửi rồi
                continue
            yield json.loads(meta), [json.loads(e) for e in entries]
