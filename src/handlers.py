from telegram import Chat, Message, Update
from telegram.ext import ContextTypes

from src import services
from src.db.crud import get_async_session, user_crud
from src.settings import DESCRIPTION


async def track_chats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверяет чаты бота."""
    get_session = get_async_session()
    session = await get_session.__anext__()

    my_chat = update.my_chat_member
    current_status = my_chat.new_chat_member.status
    previous_status = my_chat.old_chat_member.status

    if my_chat.chat.type in Chat.PRIVATE:
        if current_status != previous_status:
            await services.check_private_chat_status(my_chat, current_status, session)

    if my_chat.chat.type in Chat.CHANNEL:
        await services.check_channel_chat(my_chat, current_status, previous_status, session, context)


async def posting_message_handler(message: Message, channel_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Публикует вложение из сообщения пользователя в канал."""
    if message.animation:
        await context.bot.send_animation(
            chat_id=channel_id,
            animation=message.animation.file_id,
            caption=DESCRIPTION,
        )
    elif message.photo:
        await context.bot.send_photo(chat_id=channel_id, photo=message.photo[0].file_id, caption=DESCRIPTION)
    else:
        await context.bot.send_video(chat_id=channel_id, video=message.video.file_id, caption=DESCRIPTION)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Парсит фото, видео и анимацию из сообщения от пользователя."""
    get_session = get_async_session()
    session = await get_session.__anext__()
    user_db = await user_crud.get_user(update.effective_user.id, session)
    for channel in user_db.channels:
        if channel and channel.is_active is True:
            channel_id = channel.channel_id
            await posting_message_handler(update.message, channel_id, context)
