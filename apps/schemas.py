# from datetime import date
# from pydantic import BaseModel, EmailStr  # pip install pydantic[email]
# from enum import Enum
# from fastapi import Form
#
#
# class UserSchema(BaseModel):
#     email: EmailStr
#     username: str
#     password: str
#
#     class Config:
#         orm_mode = True
#
#
# class Roles(Enum):
#     user = "user"
#     admin = "admin"
from pydantic import BaseModel


class UserData(BaseModel):
    id: int | None = None
    email: str
    name: str | None = None
    is_active: bool | None = None


class UserInDB(UserData):
    password: str
