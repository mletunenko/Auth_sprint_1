from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.oauth import OAuthAccount, OAuthProvider


async def get_provider_by_name(
    name: str,
    session: AsyncSession,
) -> OAuthProvider:
    result = await session.execute(select(OAuthProvider).where(OAuthProvider.name == name))
    provider = result.scalars().first()
    return provider


async def save_oauth_account(
    user_id: UUID4,
    provider_id: UUID4,
    provider_user_id,
    token_data: dict,
    session: AsyncSession,
) -> OAuthAccount:
    oauth_account = await get_oauth_account(
        user_id,
        provider_id,
        session,
    )
    if oauth_account:
        oauth_account.access_token = token_data["access_token"]
        oauth_account.refresh_token = token_data["refresh_token"]
        oauth_account.expires_at = token_data["expires_in"]
        await session.commit()
    else:
        oauth_account = await create_oauth_account(
            user_id,
            provider_id,
            provider_user_id,
            token_data,
            session,
        )
    return oauth_account


async def create_oauth_account(
    user_id: UUID4,
    provider_id: UUID4,
    provider_user_id: str,
    token_data: dict,
    session: AsyncSession,
) -> OAuthAccount:
    oauth_account = OAuthAccount(
        user_id=user_id,
        provider_id=provider_id,
        provider_user_id=provider_user_id,
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
    )
    session.add(oauth_account)
    await session.commit()
    return oauth_account


async def get_oauth_account(
    user_id: UUID4,
    provider_id: UUID4,
    session: AsyncSession,
) -> OAuthAccount:
    result = await session.execute(
        select(OAuthAccount).where(OAuthAccount.user_id == user_id).where(OAuthAccount.provider_id == provider_id)
    )
    oauth_account = result.scalars().first()
    return oauth_account


async def get_user_by_provider_user_id(
    provider_user_id: str,
    session: AsyncSession,
) -> User | None:
    result = await session.execute(
        select(User).join(OAuthAccount).where(OAuthAccount.provider_user_id == provider_user_id)
    )
    return result.scalars().first()
