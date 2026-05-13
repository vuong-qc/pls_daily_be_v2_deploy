from datetime import datetime
from typing import List, Optional

from beanie import Document, Indexed, before_event, Insert
# from src.models.counter.counter_document import CounterDocument


class UserDocument(Document):
    dob: Optional[datetime] = None
    avt: str = ""
    email: str
    name: str
    phone: Optional[str] = None
    password: str
    roles: List[int]
    require_pass_update: bool = True
    status: int = 0
    gender: int
    traineeStatus: int
    address: Optional[str] = None
    # user_code: int = Indexed(unique=True)
    created_at: int
    updated_at: int

    # @before_event(Insert)
    # async def gen_user_code(self):
    #     counter = await CounterDocument.find_one({CounterDocument.name : "users"})
    #     if not counter:
    #         counter = CounterDocument(name= "users", last_value=1001)
    #         await counter.insert()
    #         self.user_code = 1001
    #     else:
    #         new_value = counter.last_value + 1
    #         if new_value > 9999:
    #             raise ValueError("Reach limit 9999 code")
    #         counter.last_value = new_value
    #         await counter.save()
    #         self.user_code = new_value


    class Settings:
        name = "users"