from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class UserBaseOut(BaseModel):
    login: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None

class UserIn(UserBaseOut):
    password: str

class UserOut(UserBaseOut):
    id: UUID4
    created_at: datetime

