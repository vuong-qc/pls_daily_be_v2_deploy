from src.repositories.user.user_repository import UserRepository
from src.models.user.user_document import UserDocument
from src.utils.security_password_util import SecurityPasswordUtil
from src.enums.user_status_enum import UserStatusEnum
from beanie.operators import Set, RegEx, In, Or
from bson import ObjectId
from src.models.user.response.user_response_model import UserResponse, UserDetails
class BeanieUserRepository(UserRepository):
    async def create_user(self, user_data: dict):
        hashed_password = SecurityPasswordUtil.hash_password(user_data["password"])
        user_data["password"] = hashed_password
        user_doc = UserDocument(**user_data)
        await user_doc.insert()
        user_response = user_doc.model_dump(mode="json")
        return UserResponse.model_validate(user_response)

    async def get_user_by_email(self, email: str):
        user_doc = await UserDocument.find_one(UserDocument.email == email,UserDocument.status == UserStatusEnum.ACTIVE.value)
        if user_doc:
            user_response = user_doc.model_dump(mode="json")
            # print("user_response:", user_response)
            return UserResponse.model_validate(user_response)
        return None
    async def get_user_by_id(self, user_id: str, is_internal: bool =False):
        if not ObjectId.is_valid(user_id):
            return None
        user_data = await UserDocument.get(user_id)
        if user_data and user_data.status != UserStatusEnum.DELETED.value:
            user_response = user_data.model_dump(mode="json")
            # print("user_response:", user_response)
            return UserResponse.model_validate(user_response)
        return None

    async def update_user(self, user_id:str, user_data: dict):
        user_doc = await UserDocument.get(user_id)
        if user_doc:
            if user_data.get("password"):
                user_data["password"] = SecurityPasswordUtil.hash_password(user_data.pop("password"))
            await user_doc.update(Set(user_data))
            user_response = user_doc.model_dump(mode="json")
            return UserResponse.model_validate(user_response)
        return None

    async def get_list_users(self, filters: dict):
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
        if filters.get("status") is not None:
            # print("status:", filters["status"])
            status = filters.pop("status")
            filters.update(In(UserDocument.status, [status]))
        else:
            filters.update(In(UserDocument.status, [UserStatusEnum.ACTIVE.value, UserStatusEnum.INACTIVE.value]))
        query = UserDocument.find(filters,fetch_links=True)
        count = await query.count()
        list_user_doc = await query.skip(offset).limit(limit).sort("-created_at").to_list()
        list_users = []
        # print("list_users:", list_user_doc)
        for user in list_user_doc:
            # user_response = user.model_dump(mode="json")
            # print("user_response:", user)
            list_users.append(UserDetails.model_validate(user))
        return list_users, count

    async def validate_password(self, password: str, user_id:str) -> bool:
        user = await UserDocument.find_one(UserDocument.id == user_id)
        if user:
            is_valid = SecurityPasswordUtil.verify_password(
                password,
                user.password
            )
            return is_valid
        return False