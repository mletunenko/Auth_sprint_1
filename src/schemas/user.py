from datetime import date

from fastapi import Depends
from pydantic import UUID4, BaseModel, EmailStr

from schemas.base import PaginationParams
from schemas.token import TokenInfo


class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None


class UserLoginIn(BaseModel):
    email: EmailStr
    password: str


class UserLoginOut(TokenInfo):
    id: UUID4
    email: EmailStr
    role: str | None = None


class UserAccountOut(BaseModel):
    id: UUID4
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None


class UserListParams(BaseModel):
    birth_date: date | None = None
    pagination: PaginationParams = Depends()
