import datetime

from sqlalchemy.orm import mapped_column, Mapped

from utils.password import generate_password_hash, check_password_hash
from .base import Base

class User(Base):
    login: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(datetime.UTC))

    def __init__(self, login: str, email: str, password:str, first_name: str, last_name: str) -> None:
        self.login = login
        self.email = email
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(password, self.password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'