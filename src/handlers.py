from telegram import Chat, Update
from telegram.ext import CallbackContext, ContextTypes

from src import services
from src.db.base import user_manager


async def start(update: Update, context: CallbackContext) -> None:
    """Команда /start."""
    start_text = (
        "Бот публикует вложения из полученных сообщений в ваш канал.\n"
        "Как работать с ботом:\n"
        "1) Добавьте бота в свой канал с правами публикации сообщений (работает только с каналами)\n"
        "2) Отправьте боту любое сообщение с видео/фото либо анимацией (одиночной)\n"
        "3) Бот опубликует это вложение в вашем канале от имени канала"
    )
    await services.get_or_create_or_update_user(update.effective_user)
    await context.bot.send_message(chat_id=update.effective_user.id, text=start_text)


async def track_chats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает обновления чатов Telegram."""
    if update.my_chat_member.chat.type in Chat.PRIVATE:
        await services.check_private_chat_status(update)

    if update.my_chat_member.chat.type in Chat.CHANNEL:
        await services.check_channel_chat(update, context.bot)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Парсит фото, видео и анимацию из полученного сообщения."""
    user = await user_manager.get_user(update.effective_user.id)

    for channel in user.channels:
        if channel and channel.is_active is True:
            channel_id = channel.channel_id
            await services.posting_message(update.message, channel_id, context.bot)
