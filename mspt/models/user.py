from typing import Optional

from pydantic import BaseModel


# Shared properties
class UserBase(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserBaseInDB(UserBase):
    uid: int

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    email: str
    password: str


class UserUpdate(UserBaseInDB):
    password: Optional[str] = None
    email: Optional[str] = None


# Additional properties to return via API
class User(UserBaseInDB):
    pass


# Additional properties stored in DB
class UserInDB(UserBaseInDB):
    hashed_password: str


# Login Exras
class UserLoginExtras(BaseModel):
    uid: int
    first_name: str
    last_name: str
    is_active: bool
    is_superuser: bool
