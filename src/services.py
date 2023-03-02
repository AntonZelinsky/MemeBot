from telegram import Bot, Chat, ChatMember, Message, Update
from telegram import User as TelegramUser

from src.db.base import channel_manager, user_manager
from src.db.models import Channel, User
from src.settings import DESCRIPTION


async def get_or_create_or_update_user(telegram_user: TelegramUser) -> User:
    """Получает информацию из update и на её основании возвращает пользователя.

    Если пользователя с такими данными нет - создает пользователя,
    если пользователь есть - обновляет информацию о нем в БД.
    """
    user = await user_manager.get_user(telegram_user.id)

    if user:
        user = await update_user(telegram_user, user.id)
    else:
        user = await create_user(telegram_user)
    return user


async def update_user(telegram_user: TelegramUser, user_id: int) -> User:
    """Обновляет данные пользователя из update."""
    parse_user = User.from_parse(telegram_user)
    return await user_manager.update(user_id, parse_user)


async def create_user(telegram_user: TelegramUser) -> User:
    """Создает пользователя по данным из update."""
    parse_user = User.from_parse(telegram_user)
    return await user_manager.create(parse_user)


async def check_private_chat_status(update: Update) -> None:
    """Проверяет статус бота в приватном чате."""
    current_status, _ = get_chat_status(update)
    if current_status in ChatMember.BANNED:
        user = await user_manager.get_user(update.effective_user.id)
        await deactivate(instance=user)


def get_chat_status(update: Update) -> tuple[str, str]:
    current_status = update.my_chat_member.new_chat_member.status
    previous_status = update.my_chat_member.old_chat_member.status
    return current_status, previous_status


async def deactivate(instance) -> None:
    """Изменяет статус is_active у instance."""
    instance.is_active = False
    if isinstance(instance, User):
        await user_manager.update(instance.id, instance)
    elif isinstance(instance, Channel):
        await channel_manager.update(instance.id, instance)


async def check_channel_chat(update: Update, telegram_bot: Bot) -> None:
    """Сканирует изменения чата каналов из update."""
    channel = await check_channel_chat_status(update)
    message = create_message(update)
    await send_notify_message(channel, message, telegram_bot)


async def check_channel_chat_status(update: Update) -> Channel:
    """Проверяет статус бота в чате канала."""
    current_status, previous_status = get_chat_status(update)
    chat = update.my_chat_member.chat

    if current_status in ChatMember.BANNED or current_status in ChatMember.LEFT:
        channel = await channel_manager.get_channel(chat.id)
        if channel:
            await deactivate(instance=channel)
    elif previous_status in ChatMember.BANNED or previous_status in ChatMember.LEFT:
        user = await user_manager.get_user(update.effective_user.id)
        channel = await create_channel(chat, user.id)
    else:
        channel = await channel_manager.get_channel(chat.id)
    return channel


async def create_channel(chat: Chat, user_id: int) -> Channel:
    """Создает канал по данным из update."""
    parse_channel = Channel.from_parse(chat, user_id)
    return await channel_manager.create(parse_channel)


def create_message(update: Update) -> str:
    """Создает сообщение - уведомление о статусе бота в канале."""
    text = ""
    current_status, previous_status = get_chat_status(update)
    my_chat = update.my_chat_member

    if current_status in ChatMember.BANNED or current_status in ChatMember.LEFT:
        return f"Бот удален из канала '{my_chat.chat.title}'."
    elif previous_status in ChatMember.BANNED or previous_status in ChatMember.LEFT:
        text = f"Бот добавлен в канал '{my_chat.chat.title}',"
    elif current_status == previous_status:
        text = f"У бота в канале '{my_chat.chat.title}' изменены права,"
    rights_text = check_bot_posting_rights(my_chat.new_chat_member)
    return text + rights_text


def check_bot_posting_rights(current_channel_chat: ChatMember) -> str:
    """Проверяет у бота доступ к публикации сообщений в канале."""
    text = "отправки сообщений в группу!"
    if current_channel_chat.can_post_messages is True:
        text = " есть права для " + text
    else:
        text = " отсутствуют права для " + text
    return text


async def send_notify_message(channel: Channel, message: str, telegram_bot: Bot) -> None:
    """Отправляет сообщение об изменении статуса бота в канале пользователю, который его добавил в канал."""
    if channel and channel.user.is_active:
        await telegram_bot.send_message(chat_id=channel.user.account_id, text=message)


async def posting_message(message: Message, channel_id: int, telegram_bot: Bot) -> None:
    """Публикует вложение из сообщения в каналы пользователя."""
    if message.animation:
        await telegram_bot.send_animation(
            chat_id=channel_id,
            animation=message.animation.file_id,
            caption=DESCRIPTION,
        )
    elif message.photo:
        await telegram_bot.send_photo(chat_id=channel_id, photo=message.photo[0].file_id, caption=DESCRIPTION)
    elif message.video:
        await telegram_bot.send_video(chat_id=channel_id, video=message.video.file_id, caption=DESCRIPTION)
