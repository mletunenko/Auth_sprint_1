from datetime import datetime

from pydantic import BaseModel, EmailStr, UUID4


class UserBase(BaseModel):
    login: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID4
    created_at: datetime
