from pydantic import UUID4
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base


class OAuthProvider(Base):
    __tablename__ = "oauth_providers"

    name: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<OAuthProvider {self.name}>"


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    user_id: Mapped[UUID4] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider_id: Mapped[[UUID4]] = mapped_column(ForeignKey("oauth_providers.id", ondelete="CASCADE"))
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[int] = mapped_column(nullable=True)

    user = relationship('User', back_populates='oauth_accounts')