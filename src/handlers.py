from telegram import Chat, Update
from telegram.ext import ContextTypes

from src import services
from src.db.crud import user_crud


async def track_chats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверяет чаты бота."""
    my_chat = update.my_chat_member
    current_status = my_chat.new_chat_member.status
    previous_status = my_chat.old_chat_member.status

    if (my_chat.chat.type in Chat.PRIVATE) and (current_status != previous_status):
        await services.check_private_chat_status(my_chat, current_status)

    if my_chat.chat.type in Chat.CHANNEL:
        await services.check_channel_chat(my_chat, current_status, previous_status, context)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Парсит фото, видео и анимацию из сообщения от пользователя."""
    user_db = await user_crud.get_user(update.effective_user.id)
    for channel in user_db.channels:
        if channel and channel.is_active is True:
            channel_id = channel.channel_id
            await services.posting_message(update.message, channel_id, context)
