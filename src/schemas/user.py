from fastapi import Depends
from pydantic import UUID4, BaseModel, EmailStr, Field

from schemas.base import PaginationParams
from schemas.token import TokenInfo


class UserIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID4
    email: EmailStr


class UserTokensOut(TokenInfo):
    id: UUID4
    email: EmailStr


class UserListParams(BaseModel):
    birth_day: int | None = Field(None, description="День даты рождения", ge=1, le=31)
    birth_month: int | None = Field(None, description="Месяц даты рождения", ge=1, le=12)
    pagination: PaginationParams = Depends()
