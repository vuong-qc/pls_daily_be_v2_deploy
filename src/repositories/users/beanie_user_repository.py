from src.repositories.users.user_repository import UserRepository
from src.documents.user_document import UserDocument
from src.utils.security_password_util import SecurityPasswordUtil
from src.enums.user_status_enum import UserStatusEnum
from beanie.operators import Set, RegEx, In, Or
from bson import ObjectId
class BeanieUserRepository(UserRepository):
    async def create_user(self, user_data: dict) -> dict:
        hashed_password = SecurityPasswordUtil.hash_password(user_data["password"])
        user_data["password"] = hashed_password
        user_doc = UserDocument(**user_data)
        await user_doc.insert()
        user_response = user_doc.model_dump(exclude={"password"})
        user_response["id"] = str(user_response.pop("id"))
        return user_response

    async def get_user_by_email(self, email: str) -> dict | None:
        user_doc = await UserDocument.find_one(UserDocument.email == email,UserDocument.status == UserStatusEnum.ACTIVE.value)
        if user_doc:
            user_response = user_doc.model_dump()
            user_response["id"] = str(user_response.pop("id"))
            return user_response
        return None
    async def get_user_by_id(self, user_id: str, is_internal: bool =False) -> dict | None:
        if not ObjectId.is_valid(user_id):
            return None
        user_data = await UserDocument.get(user_id)
        if user_data and user_data.status == UserStatusEnum.ACTIVE.value:
            if is_internal:
                user_response = user_data.model_dump()
            else:
                user_response = user_data.model_dump(exclude={"password"})
            user_response["id"] = str(user_response.pop("id"))
            return user_response
        return None

    async def update_user(self, user_id:str, user_data: dict) -> dict| None:
        user_doc = await UserDocument.get(user_id)
        if user_doc:
            await user_doc.update(Set(user_data))
            user_response = user_doc.model_dump(exclude={"password"})
            user_response["id"] = str(user_response.pop("id"))
            return user_response
        return None

    async def get_list_users(self, filters: dict) -> tuple[list[dict], int]:
        offset = filters.pop("offset", 0)
        limit = filters.pop("limit", 10)
        if filters.get("roles"):
            roles = filters.pop("roles")
            filters.update(In(UserDocument.roles, roles))
        if filters.get("keyword"):
            keyword = filters.pop("keyword")
            filters.update(
                Or(
                    RegEx(UserDocument.name, keyword.strip(), "i"),
                    RegEx(UserDocument.email, keyword.strip(), "i"),
                )
            )
        if filters.get("status"):
            status = filters.pop("status")
            filters.update(In(UserDocument.status, [status]))
        else:
            filters.update(In(UserDocument.status, [UserStatusEnum.ACTIVE.value, UserStatusEnum.INACTIVE.value]))
        query = UserDocument.find(filters)
        count = await query.count()
        list_user_doc = await query.skip(offset).limit(limit).sort("-created_at").to_list()
        list_users = []
        for user in list_user_doc:
            user_response = user.model_dump(exclude={"password"})
            user_response["id"] = str(user_response.pop("id"))
            list_users.append(user_response)
        return list_users, count
