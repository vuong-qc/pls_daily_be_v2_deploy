from pydantic import BaseModel, EmailStr

class LoginModel(BaseModel):
    email: str
    password: str