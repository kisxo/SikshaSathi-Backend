from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    user_full_name: str = Field(min_length=5, max_length=30)
    user_email: EmailStr
    user_phone: str = Field(max_length=10)

class UserPublic(UserBase):
    user_id: int
    user_is_admin: bool
    user_data: bool

class UsersPublic(BaseModel):
    data: list[UserPublic]

class UserCreate(UserBase):
    user_password: str

class User(UserBase):
    user_hashed_password: str

class UserUpdate(BaseModel):
    user_full_name: str = Field(min_length=5, max_length=30)
    user_phone: str = Field(max_length=10)
    user_email: EmailStr
    user_password: str