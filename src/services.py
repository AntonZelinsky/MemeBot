from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Chat, ChatMember, User

from src.db.crud import channel_crud, user_crud


def user_parser(user: User) -> dict:
    """Парсит данные пользователя."""
    parsed_user = {
        "account_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name or None,
        "username": user.username or None,
    }
    return parsed_user


def channel_parser(chat: Chat, user_id: int) -> dict:
    """Парсит данные канала."""
    channel = {
        "channel_id": chat.id,
        "title": chat.title,
        "username": chat.username or None,
        "invited_user_id": user_id,
    }
    return channel


async def activate_user(user_id: int, session: AsyncSession, status: bool = True):
    """Изменяет статус is_active у пользователя."""
    is_active = {"is_active": status}
    await user_crud.update(user_id, is_active, session)


async def deactivate_channel(channel_id: int, session: AsyncSession):
    """Изменяет статус is_active у канала на False."""
    is_active = {"is_active": False}
    await channel_crud.update(channel_id, is_active, session)


def check_bot_privileges(current_channel_chat: ChatMember) -> str:
    """Проверяет у бота доступ к постингу сообщений в канале."""
    text = "отправки сообщений в группу!"
    if current_channel_chat.can_post_messages is True:
        text = " есть права для " + text
    else:
        text = " отсутствуют права для " + text
    return text
