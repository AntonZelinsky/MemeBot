from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Chat, User

from src.db import channel_crud, user_crud


def user_parser(user: User) -> dict:
    """Парсит данные пользователя из чата."""
    parsed_user = {
        "account_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name or None,
        "username": user.username or None,
    }
    return parsed_user


def channel_parser(chat: Chat, user: User) -> dict:
    """Парсит данные канала из чата."""
    channel = {
        "channel_id": chat.id,
        "title": chat.title,
        "username": chat.username or None,
        "invited_user_id": user.id,
    }
    return channel


async def activate_user(user_id: int, session: AsyncSession, status: bool = True):
    """Изменяет статус is_active у пользователя."""
    is_active = {"is_active": status}
    await user_crud.update(user_id, is_active, session)


async def deactivate_channel(channel_id: int, session: AsyncSession):
    """Изменяет статус is_active у канала на False."""
    is_active = {"is_active": False}
    channel_db = await channel_crud.get_channel(channel_id, session)
    if channel_db:
        await channel_crud.update(channel_db, is_active, session)
        return channel_db
