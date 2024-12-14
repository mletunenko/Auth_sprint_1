from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class UserBaseOut(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None

class UserCreateIn(UserBaseOut):
    password: str

class UserReadOut(UserBaseOut):
    id: UUID4
    created_at: datetime

