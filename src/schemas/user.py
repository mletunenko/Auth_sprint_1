from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class UserBaseOut(BaseModel):
    email: EmailStr


class UserFullOut(UserBaseOut):
    first_name: str | None = None
    last_name: str | None = None

class UserIn(UserBaseOut):
    password: str

class UserOut(UserBaseOut):
    id: UUID4
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserAccountOut(BaseModel):
    id: UUID4
    email: EmailStr
    password: str = '***********'


class UserIdOut(BaseModel):
    id: UUID4


class UserAccountLogin(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID4

    class Config:
        orm_mode = True
