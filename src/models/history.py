import datetime
import uuid
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class LoginHistory(Base):
    __tablename__ = "login_history"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    timestamp: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc)
    )
    ip_address: Mapped[str] = mapped_column(nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return (f"<LoginHistory user_id={self.user_id}, "
                f"timestamp={self.timestamp}, "
                f"ip_address={self.ip_address}, user_agent={self.user_agent}>")
