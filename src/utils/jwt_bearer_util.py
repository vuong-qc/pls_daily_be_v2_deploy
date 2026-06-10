import jwt
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.configs import settings
from datetime import datetime, timedelta, timezone


class JWTBearerUtil(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearerUtil, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearerUtil, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")

            payload = self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired token.")

            return payload
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jwt_token: str):
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except:
            return None

    @staticmethod
    def generate_access_token(user_id: str, roles: list, updated_at: int)->str:
        payload = {
            "sub": user_id,
            "roles": roles,
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=7),
            "updated_at": updated_at,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token