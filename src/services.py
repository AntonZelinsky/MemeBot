import telegram
import telegram.ext

from src import exceptions
from src.constants import constants
from src.db import base, models


async def create_user(telegram_user: telegram.User) -> None:
    """Запускает парсер update и создание пользователя из полученных данных."""
    parse_user = models.User.from_parse(telegram_user.to_dict())
    try:
        await base.user_repository.create(parse_user)
    except exceptions.ObjectAlreadyExistsError:
        pass


async def create_channel(telegram_chat: telegram.Chat) -> None:
    """Запускает парсер update и создание канала из полученных данных."""
    parse_channel = models.Channel.from_parse(telegram_chat.to_dict())
    try:
        await base.channel_repository.create(parse_channel)
    except exceptions.ObjectAlreadyExistsError:
        pass


async def user_is_admin_in_channel(update: telegram.Update, telegram_bot: telegram.Bot) -> None:
    """Проверяет, является ли текущий пользователь администратором канала, из которого переслали сообщение."""
    user_id = update.effective_user.id
    channel_id = update.message.forward_from_chat.id
    try:
        channel_admins = await telegram_bot.get_chat_administrators(chat_id=channel_id)
    except telegram.error.Forbidden as e:
        raise exceptions.BotKickedFromTheChannel(channel_id) from e

    for admin in channel_admins:
        if admin.user.id == user_id:
            return
    raise exceptions.UserIsNotAdminInChannel(user_id, channel_id)


async def create_bind(user_id: int, channel_id: int) -> None:
    """Создает связь аккаунта пользователя и канала."""
    new_bind = models.Bind.new_bind(user_id, channel_id)
    await base.bind_repository.create(new_bind)


async def change_bind_description(new_description: str, user_data: telegram.ext.CallbackContext) -> None:
    """Изменяет текст сообщения для постов в выбранном канале."""
    user = user_data[constants.CURRENT_USER]
    channel = user_data[constants.CURRENT_CHANNEL]
    await base.bind_repository.update_description(user.id, channel.id, new_description)


async def posting_message(bind: models.Bind, message: telegram.Message, telegram_bot: telegram.Bot) -> None:
    """Публикует вложение из сообщения в канал пользователя с необходимым текстом сообщения."""
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
