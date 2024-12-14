import datetime

from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False, default="")
    last_name: Mapped[str] = mapped_column(nullable=False, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc))

    def set_password(self, raw_password: str) -> None:
        self.password = pbkdf2_sha256.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return pbkdf2_sha256.verify(self.password, raw_password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
