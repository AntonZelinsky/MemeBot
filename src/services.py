from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Chat

from src.db import channel_crud, user_crud
from src.models import User


def user_parser(chat: Chat) -> dict:
    """Парсит данные пользователя из чата."""
    user = {
        "account_id": chat.id,
        "first_name": chat.first_name,
        "last_name": chat.last_name or None,
        "username": chat.username or None,
    }
    return user


def channel_parser(chat: Chat, user: User) -> dict:
    """Парсит данные канала из чата."""
    channel = {
        "channel_id": chat.id,
        "title": chat.title,
        "username": chat.username or None,
        "invited_user_id": user.id,
    }
    return channel


async def activate_user(account_id: int, session: AsyncSession, status: bool = True):
    """Изменяет статус is_active у пользователя."""
    is_active = {"is_active": status}
    user_db = await user_crud.get_user(account_id, session)
    if user_db:
        await user_crud.update(user_db, is_active, session)


async def deactivate_channel(channel_id: int, session: AsyncSession):
    """Изменяет статус is_active у канала на False."""
    is_active = {"is_active": False}
    channel_db = await channel_crud.get_channel(channel_id, session)
    if channel_db:
        await channel_crud.update(channel_db, is_active, session)
        return channel_db
