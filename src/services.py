import telegram

from src import settings
from src.db import base, models


async def create_user(telegram_user: telegram.User) -> models.User:
    """Создает пользователя из данных update."""
    parse_user = models.User.from_parse(telegram_user.to_dict())
    user = await base.user_repository.create(parse_user)
    return user


async def create_channel(telegram_chat: telegram.Chat) -> models.Channel:
    parse_channel = models.Channel.from_parse(telegram_chat.to_dict())
    channel = await base.channel_repository.create(parse_channel)
    return channel


async def update_channel(telegram_chat: telegram.Chat, channel: models.Channel) -> models.Channel:
    parse_channel = models.Channel.from_parse(telegram_chat.to_dict())
    channel = await base.channel_repository.update(channel.id, parse_channel)
    return channel


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
