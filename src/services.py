from typing import Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Chat, ChatMember, ChatMemberUpdated, User

from src.db.crud import channel_crud, user_crud

DatabaseModel = TypeVar("DatabaseModel")


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


async def activate_user(user_id: int, session: AsyncSession, status: bool = True) -> None:
    """Изменяет статус is_active у пользователя."""
    is_active = {"is_active": status}
    await user_crud.update(user_id, is_active, session)


async def deactivate_channel(channel_id: int, session: AsyncSession) -> None:
    """Изменяет статус is_active у канала на False."""
    is_active = {"is_active": False}
    await channel_crud.update(channel_id, is_active, session)


def check_bot_privileges(current_channel_chat: ChatMember, current_status) -> str:
    """Проверяет у бота доступ к постингу сообщений в канале."""
    if current_status in [ChatMember.BANNED, ChatMember.LEFT]:
        return ""
    text = "отправки сообщений в группу!"
    if current_channel_chat.can_post_messages is True:
        text = " есть права для " + text
    else:
        text = " отсутствуют права для " + text
    return text


async def create_channel(my_chat, user_id, session) -> None:
    """Создает канал по данным из обновления."""
    current_channel_data = channel_parser(my_chat.chat, user_id)
    await channel_crud.create(current_channel_data, session)


async def check_channel_chat_status(current_status, previous_status, my_chat, session) -> Optional[DatabaseModel]:
    """Проверяет статус чата канала и обновляет информацию о канале в БД."""
    if current_status in ChatMember.ADMINISTRATOR and current_status != previous_status:
        user_id = await get_or_create_or_update_user(my_chat, session)
        await create_channel(my_chat, user_id, session)
    if current_status in [ChatMember.BANNED, ChatMember.LEFT]:
        channel_db = await channel_crud.get_channel(my_chat.chat.id, session)
        if channel_db:
            await deactivate_channel(channel_db.id, session)
            return channel_db


def create_message(current_status, previous_status, my_chat) -> str:
    """Создает сообщение - уведомление о статусе бота в канале."""
    text = ""
    rights_text = check_bot_privileges(my_chat.new_chat_member, current_status)
    if current_status in ChatMember.ADMINISTRATOR and current_status != previous_status:
        text = f"Бот добавлен в канал '{my_chat.chat.title}',"
    elif current_status == previous_status:
        text = f"У бота в канале '{my_chat.chat.title}' изменены права,"
    elif current_status in [ChatMember.BANNED, ChatMember.LEFT]:
        message = f"Бот удален из канала '{my_chat.chat.title}'"
        return message
    message = text + rights_text
    return message


async def send_notify_message(channel_db, message, context) -> None:
    """Отправляет сообщение об изменении статуса бота в канале пользователю, который его добавил в канал."""
    if channel_db and channel_db.user.is_active:
        await context.bot.send_message(chat_id=channel_db.user.account_id, text=message)


async def get_user(my_chat_member: ChatMemberUpdated, session: AsyncSession) -> Optional[DatabaseModel]:
    """Получает объект User из базы по его account_id из обновления."""
    account_id = my_chat_member.from_user.id
    user_db = await user_crud.get_user(account_id, session)
    return user_db


async def update_user(my_chat_member: ChatMemberUpdated, user_id: int, session: AsyncSession) -> None:
    """Обновляет данные пользователя."""
    current_user_data = user_parser(my_chat_member.from_user)
    await user_crud.update(user_id, current_user_data, session)


async def create_user(my_chat_member: ChatMemberUpdated, session: AsyncSession) -> int:
    """Создает пользователя по данным из обновления."""
    current_user_data = user_parser(my_chat_member.from_user)
    user_id = await user_crud.create(current_user_data, session)
    return user_id


async def get_or_create_or_update_user(my_chat_member: ChatMemberUpdated, session: AsyncSession) -> int:
    """Получает, обновляет, либо создает пользователя."""
    user_db = await get_user(my_chat_member, session)

    if user_db:
        user_id = user_db.id
        await update_user(my_chat_member, user_id, session)
    else:
        user_id = await create_user(my_chat_member, session)
    return user_id


async def check_private_chat_status(current_status: str, user_id: int, session: AsyncSession) -> None:
    """Проверяет статус приватного чата."""
    if current_status in ChatMember.BANNED:
        await activate_user(user_id=user_id, session=session, status=False)
    elif current_status in ChatMember.MEMBER:
        await activate_user(user_id=user_id, session=session)
