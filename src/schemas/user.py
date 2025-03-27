from datetime import date

from fastapi import Depends
from pydantic import UUID4, BaseModel, EmailStr, Field

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
    birth_day: int | None = Field(None, description="День даты рождения", ge=1, le=31)
    birth_month: int | None = Field(None, description="Месяц даты рождения", ge=1, le=12)
    pagination: PaginationParams = Depends()
