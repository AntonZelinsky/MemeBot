from typing import Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import ChatMember, ChatMemberUpdated
from telegram.ext import ContextTypes

from src.db.crud import channel_crud, user_crud
from src.db.models import Channel, User

DatabaseModel = TypeVar("DatabaseModel")

ACTIVATE = True
DEACTIVATE = False


def user_parser(my_chat: ChatMemberUpdated) -> DatabaseModel:
    """Парсит данные с чата в модель User."""
    telegram_user = my_chat.from_user
    user_data = User(
        account_id=telegram_user.id,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name or None,
        username=telegram_user.username or None,
    )
    return user_data


def channel_parser(my_chat, user_id) -> DatabaseModel:
    """Парсит данные с чата в модель Channel."""
    telegram_channel = my_chat.chat
    channel_data = Channel(
        channel_id=telegram_channel.id,
        title=telegram_channel.title,
        username=telegram_channel.username or None,
        invited_user_id=user_id,
    )
    return channel_data


async def change_activate(object: DatabaseModel, status: bool, session: AsyncSession) -> None:
    """Изменяет статус is_active у объекта."""
    object.is_active = status
    if isinstance(object, User):
        await user_crud.update(object.id, object, session)
    elif isinstance(object, Channel):
        await channel_crud.update(object.id, object, session)


def check_bot_privileges(current_channel_chat: ChatMember) -> str:
    """Проверяет у бота доступ к постингу сообщений в канале."""
    text = "отправки сообщений в группу!"
    if current_channel_chat.can_post_messages is True:
        text = " есть права для " + text
    else:
        text = " отсутствуют права для " + text
    return text


async def create_channel(my_chat, user_id, session) -> DatabaseModel:
    """Создает канал по данным из обновления."""
    current_channel_data = channel_parser(my_chat, user_id)
    channel = await channel_crud.create(current_channel_data, session)
    return channel


def create_message(current_status, previous_status, my_chat) -> str:
    """Создает сообщение - уведомление о статусе бота в канале."""
    text = ""
    if current_status in ChatMember.ADMINISTRATOR and current_status != previous_status:
        text = f"Бот добавлен в канал '{my_chat.chat.title}',"
    elif current_status == previous_status:
        text = f"У бота в канале '{my_chat.chat.title}' изменены права,"
    elif current_status in [ChatMember.BANNED, ChatMember.LEFT]:
        message = f"Бот удален из канала '{my_chat.chat.title}'"
        return message
    rights_text = check_bot_privileges(my_chat.new_chat_member)
    message = text + rights_text
    return message


async def send_notify_message(channel_db, message, context) -> None:
    """Отправляет сообщение об изменении статуса бота в канале пользователю, который его добавил в канал."""
    if channel_db and channel_db.user.is_active:
        await context.bot.send_message(chat_id=channel_db.user.account_id, text=message)


async def check_channel_chat_status(
    my_chat: ChatMemberUpdated,
    current_status: str,
    previous_status: str,
    session: AsyncSession,
) -> DatabaseModel:
    """Проверяет статус чата в канале и обновляет информации о канале в БД."""
    if current_status in ChatMember.ADMINISTRATOR and current_status != previous_status:
        user = await get_or_create_or_update_user(my_chat, session)
        channel_db = await create_channel(my_chat, user.id, session)
    elif current_status in [ChatMember.BANNED, ChatMember.LEFT]:
        channel_db = await channel_crud.get_channel(my_chat.chat.id, session)
        if channel_db:
            await change_activate(object=channel_db, status=DEACTIVATE, session=session)
    else:
        channel_db = await channel_crud.get_channel(my_chat.chat.id, session)
    return channel_db


async def check_channel_chat(
    my_chat: ChatMemberUpdated,
    current_status: str,
    previous_status: str,
    session: AsyncSession,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Проверяет обновления из каналов."""
    channel_db = await (my_chat, current_status, previous_status, session)
    message = create_message(current_status, previous_status, my_chat)
    await send_notify_message(channel_db, message, context)


async def get_user(my_chat: ChatMemberUpdated, session: AsyncSession) -> Optional[DatabaseModel]:
    """Получает объект User из базы по его account_id из обновления."""
    account_id = my_chat.from_user.id
    user = await user_crud.get_user(account_id, session)
    return user


async def update_user(my_chat: ChatMemberUpdated, user_id: int, session: AsyncSession) -> DatabaseModel:
    """Обновляет данные пользователя."""
    current_user_data = user_parser(my_chat)
    user = await user_crud.update(user_id, current_user_data, session)
    return user


async def create_user(my_chat: ChatMemberUpdated, session: AsyncSession) -> DatabaseModel:
    """Создает пользователя по данным из обновления."""
    current_user_data = user_parser(my_chat)
    user = await user_crud.create(current_user_data, session)
    return user


async def get_or_create_or_update_user(my_chat: ChatMemberUpdated, session: AsyncSession) -> DatabaseModel:
    """Получает, обновляет, либо создает пользователя."""
    user = await get_user(my_chat, session)

    if user:
        user = await update_user(my_chat, user.id, session)
    else:
        user = await create_user(my_chat, session)
    return user


async def check_private_chat_status(my_chat: ChatMemberUpdated, current_status: str, session: AsyncSession) -> None:
    """Проверяет статус приватного чата."""
    user = await get_or_create_or_update_user(my_chat, session)
    if current_status in ChatMember.BANNED:
        await change_activate(object=user, status=DEACTIVATE, session=session)
    elif current_status in ChatMember.MEMBER:
        await change_activate(object=user, status=ACTIVATE, session=session)
