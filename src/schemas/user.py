from datetime import datetime

from fastapi import Depends
from pydantic import UUID4, BaseModel, EmailStr, Field

from schemas.base import PaginationParams
from schemas.token import TokenInfo
from utils.enums import UserRoleEnum


class UserIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID4
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.BASIC
    created_at: datetime
    updated_at: datetime


class UserTokensOut(TokenInfo):
    id: UUID4
    email: EmailStr


class UserListParams(BaseModel):
    email: EmailStr | None = None
    pagination: PaginationParams = Depends()


class UserPatch(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

