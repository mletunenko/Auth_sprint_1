from pydantic import UUID4
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class OAuthProvider(Base):
    __tablename__ = "oauth_providers"

    name: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<OAuthProvider {self.name}>"


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    user_id: Mapped[UUID4] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider_id: Mapped[UUID4] = mapped_column(ForeignKey("oauth_providers.id", ondelete="CASCADE"))
    provider_user_id: Mapped[str] = mapped_column(nullable=True)
    access_token: Mapped[str] = mapped_column(nullable=True)
    refresh_token: Mapped[str] = mapped_column(nullable=True)
    expires_at: Mapped[int] = mapped_column(nullable=True)

    user = relationship("User", back_populates="oauth_accounts")
