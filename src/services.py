import telegram

from src.db import base, models


async def create_user(telegram_user: telegram.User) -> models.User:
    """Создает пользователя в БД по данным из update."""
    parse_user = models.User.from_parse(telegram_user.to_dict())
    user = await base.user_repository.create(parse_user)
    return user


async def create_channel(telegram_chat: telegram.Chat) -> models.Channel:
    """Создает канал в БД по данным из update."""
    parse_channel = models.Channel.from_parse(telegram_chat.to_dict())
    channel = await base.channel_repository.create(parse_channel)
    return channel


async def update_channel(telegram_chat: telegram.Chat, channel: models.Channel) -> models.Channel:
    """Обновляет канал в БД по данным из update."""
    parse_channel = models.Channel.from_parse(telegram_chat.to_dict())
    channel = await base.channel_repository.update(channel.id, parse_channel)
    return channel


# async def check_exist_bind(update: telegram.Update):
#     user = await base.user_repository.get_user(update.effective_user.id)
#     channel = await base.channel_repository.get_channel(update.message.forward_from_chat.id)
#     if channel:
#         binding = await base.user_channel_repository.get_bind(user.id, channel.id)


async def posting_message(bind: models.UserChannel, message: telegram.Message, telegram_bot: telegram.Bot) -> None:
    """Публикует вложение из сообщения в каналы пользователя."""
    if message.animation:
        await telegram_bot.send_animation(
            chat_id=bind.channel.channel_id,
            animation=message.animation.file_id,
            caption=bind.description,
        )
    elif message.photo:
        await telegram_bot.send_photo(
            chat_id=bind.channel.channel_id,
            photo=message.photo[0].file_id,
            caption=bind.description,
        )
    elif message.video:
        await telegram_bot.send_video(
            chat_id=bind.channel.channel_id,
            video=message.video.file_id,
            caption=bind.description,
        )
    else:
        raise telegram.error.TelegramError("Неподдерживаемый тип данных.")
