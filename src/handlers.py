from sqlalchemy import exc
from telegram import Chat, Update
from telegram.ext import CallbackContext, ContextTypes

from src import services
from src.db.base import user_repository


async def start(update: Update, context: CallbackContext) -> None:
    """Команда /start."""
    start_text = (
        "Привет. Я — Мем бот и буду помогать вам постить мемы в ваши каналы.\n"
        "Чтобы начать работу - просто добавьте бота в каналы, в которые вы хотите постить сообщения.\n"
        "Если бот уже добавлен в ваш канал другим администратором, для получения совместного доступа к боту вам "
        "необходимо связать вашу учетную запись с каналом, нажав на соответствующий пункт в меню. "
        "Если вы являетесь администратором канала, в котором присутствует бот, то вы получите возможность "
        "постить в этот канал. Боту в канале достаточно дать права на отправку сообщений."
    )
    await services.get_or_create_or_update_user(update.effective_user)
    await update.message.reply_text(text=start_text)
    # await context.bot.send_message(chat_id=update.effective_user.id, text=start_text)
    # print(f"start up={update}")
    # await menu_commands.start_menu(update, context)


async def track_chats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает обновления чатов Telegram."""
    if update.my_chat_member.chat.type in Chat.PRIVATE:
        await services.check_private_chat_status(update)

    if update.my_chat_member.chat.type in Chat.CHANNEL:
        await services.check_channel_chat(update, context.bot)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Парсит фото, видео и анимацию из полученного сообщения."""
    try:
        user = await user_repository.get_user(update.effective_user.id)
    except exc.NoResultFound:
        raise exc.NoResultFound
    for channel in user.channels:
        if channel and channel.is_active is True:
            channel_id = channel.channel_id
            await services.posting_message(update.message, channel_id, context.bot)
