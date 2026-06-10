from fastapi import HTTPException
from typing import List
from fastapi import Depends
from src.utils.jwt_bearer_util import JWTBearerUtil


class RoleCheckerUtil:
    def __init__(self, allowed_roles: List[int]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_payload: dict = Depends(JWTBearerUtil())):
        user_roles = user_payload.get("roles", [])

        has_role = any(role in self.allowed_roles for role in user_roles)

        if not has_role:
            raise HTTPException(
                status_code=403,
                detail="You don't have enough permissions to access this resource"
            )
        return user_payload