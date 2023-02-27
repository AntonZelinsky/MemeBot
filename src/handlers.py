from telegram import Chat, Update
from telegram.ext import ContextTypes

from db import base
from src import services


async def track_chats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает обновления чатов Telegram."""
    my_chat = update.my_chat_member
    telegram_user = update.effective_user
    current_status = my_chat.new_chat_member.status
    previous_status = my_chat.old_chat_member.status

    if (my_chat.chat.type in Chat.PRIVATE) and (current_status != previous_status):
        await services.check_private_chat_status(telegram_user, current_status)

    if my_chat.chat.type in Chat.CHANNEL:
        await services.check_channel_chat(telegram_user, my_chat, current_status, previous_status, context.bot)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Парсит фото, видео и анимацию из полученного сообщения."""
    user_db = await base.user_base.get_user(update.effective_user.id)
    if user_db is None:
        return
    for channel in user_db.channels:
        if channel and channel.is_active is True:
            channel_id = channel.channel_id
            await services.posting_message(update.message, channel_id, context.bot)
