import datetime

from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import TIMESTAMP, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import UserRoleEnum

from .base import Base


class User(Base):
    __tablename__ = "users"

    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum, name="role"), default=UserRoleEnum.BASIC)

    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )

    def set_password(self, raw_password: str) -> None:
        self.password = pbkdf2_sha256.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return pbkdf2_sha256.verify(raw_password, self.password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
