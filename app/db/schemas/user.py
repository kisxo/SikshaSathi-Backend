import enum
from pydantic import BaseModel, Field
from pydantic.types import datetime, date
from typing import Optional
from pydantic.types import Json


class UserBase(BaseModel):
    user_full_name: str = Field(min_length=5, max_length=30)
    user_email: str = Field(max_length=250)
    user_phone: str = Field(max_length=10)

class UserPublic(UserBase):
    user_id: int

class UsersPublic(BaseModel):
    data: list[UserPublic]

class UserCreate(UserBase):
    user_password: str

class User(UserBase):
    user_hashed_password: str

class UserUpdate(BaseModel):
    user_full_name: str = Field(min_length=5, max_length=30)
    user_phone: str = Field(max_length=10)
    user_email: str = Field(max_length=250)
    user_password: str