import telegram
from sqlalchemy import exc

from src import settings
from src.db import base, models

ACTIVATE = True
DEACTIVATE = False


async def get_or_create_or_update_user(telegram_user: telegram.User) -> models.User:
    """Получает информацию из update и на её основании возвращает пользователя.

    Если пользователя с такими данными нет - создает пользователя,
    если пользователь есть - обновляет информацию о нем в БД.
    """
    parse_user = models.User.from_parse(telegram_user.to_dict())

    try:
        user = await base.user_repository.get_user(telegram_user.id)
        user_update = change_activate(parse_user, ACTIVATE)
        user = await base.user_repository.update(user.id, user_update)
    except exc.NoResultFound:
        user = await base.user_repository.create(parse_user)
    return user


def change_activate(instance, status: bool):  # Тайпинги
    """Изменяет статус is_active у instance."""
    instance.is_active = status
    return instance


async def check_private_chat_status(update: telegram.Update) -> None:
    """Проверяет статус бота в приватном чате."""
    current_status, _ = get_chat_status(update)
    if current_status in telegram.ChatMember.BANNED:
        try:
            user = await base.user_repository.get_user(update.effective_user.id)
            user_update = change_activate(user, DEACTIVATE)
            await base.user_repository.update(user.id, user_update)
        except exc.NoResultFound:
            pass  # Придумать чем заменить


def get_chat_status(update: telegram.Update) -> tuple[str, str]:
    current_status = update.my_chat_member.new_chat_member.status
    previous_status = update.my_chat_member.old_chat_member.status
    return current_status, previous_status


async def check_channel_chat(update: telegram.Update, telegram_bot: telegram.Bot) -> None:
    """Сканирует изменения чата каналов из update."""
    await check_channel_chat_status(update)

    # channel = await check_channel_chat_status(update)
    #
    # message = create_message(update)
    # await send_notify_message(channel, message, telegram_bot)


async def check_channel_chat_status(update: telegram.Update) -> models.Channel:
    """Проверяет статус бота в чате канала."""
    current_status, previous_status = get_chat_status(update)
    chat = update.my_chat_member.chat

    if current_status in telegram.ChatMember.BANNED or current_status in telegram.ChatMember.LEFT:
        try:
            channel = await base.channel_repository.get_channel(chat.id)
            channel_update = change_activate(channel, DEACTIVATE)
            channel = await base.channel_repository.update(channel.id, channel_update)
        except exc.NoResultFound:
            raise exc.NoResultFound  # Придумать чем заменить
    elif previous_status in telegram.ChatMember.BANNED or previous_status in telegram.ChatMember.LEFT:
        parse_channel = models.Channel.from_parse(update.my_chat_member.chat.to_dict())
        try:
            channel = await base.channel_repository.get_channel(chat.id)
            channel_update = change_activate(parse_channel, ACTIVATE)
            channel = await base.channel_repository.update(channel.id, channel_update)
        except exc.NoResultFound:
            channel = await base.channel_repository.create(parse_channel)
        user = await base.user_repository.get_user(update.effective_user.id)  # Здесь может вылететь
        new_bind = models.UserChannel.new_bind(user.id, channel.id)
        await base.user_channel_repository.create(new_bind)
    else:
        channel = await base.channel_repository.get_channel(chat.id)  # Здесь может вылететь
    return channel


# async def create_channel(update: telegram.Update) -> models.Channel:
#     """Создает канал по данным из update."""
#     user = await base.user_repository.get_user(update.effective_user.id)
#     parse_channel = models.Channel.from_parse(update.my_chat_member.chat.to_dict())
#     return await base.channel_repository.create(parse_channel)


def create_message(update: telegram.Update) -> str:
    """Создает сообщение - уведомление о статусе бота в канале."""
    text = ""
    current_status, previous_status = get_chat_status(update)
    my_chat = update.my_chat_member

    if current_status in telegram.ChatMember.BANNED or current_status in telegram.ChatMember.LEFT:
        return f"Бот удален из канала '{my_chat.chat.title}'."
    elif previous_status in telegram.ChatMember.BANNED or previous_status in telegram.ChatMember.LEFT:
        text = f"Бот добавлен в канал '{my_chat.chat.title}',"
    elif current_status == previous_status:
        text = f"У бота в канале '{my_chat.chat.title}' изменены права,"
    rights_text = bot_posting_rights_message(my_chat.new_chat_member.can_post_messages)
    return text + rights_text


def bot_posting_rights_message(can_post: bool) -> str:
    """Проверяет у бота доступ к публикации сообщений в канале."""
    text = "отправки сообщений в группу!"
    if can_post is True:
        text = " есть права для " + text
    else:
        text = " отсутствуют права для " + text
    return text


async def send_notify_message(channel: models.Channel, message: str, telegram_bot: telegram.Bot) -> None:
    """Отправляет сообщение об изменении статуса бота в канале пользователю, который его добавил в канал."""
    if channel.user.is_active:
        await telegram_bot.send_message(chat_id=channel.user.account_id, text=message)


async def posting_message(message: telegram.Message, channel_id: int, telegram_bot: telegram.Bot) -> None:
    """Публикует вложение из сообщения в каналы пользователя."""
    if message.animation:
        await telegram_bot.send_animation(
            chat_id=channel_id,
            animation=message.animation.file_id,
            caption=settings.DESCRIPTION,
        )
    elif message.photo:
        await telegram_bot.send_photo(
            chat_id=channel_id,
            photo=message.photo[0].file_id,
            caption=settings.DESCRIPTION,
        )
    elif message.video:
        await telegram_bot.send_video(
            chat_id=channel_id,
            video=message.video.file_id,
            caption=settings.DESCRIPTION,
        )
    else:
        raise telegram.error.TelegramError("Неподдерживаемый тип данных.")
