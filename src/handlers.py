from telegram import Chat, ChatMember, Update
from telegram.ext import CallbackContext, ContextTypes

from src import services
from src.constants import constants
from src.db import base


async def start(update: Update, context: CallbackContext) -> None:
    """Команда /start."""
    start_text = (
        "Привет. Я — Мем бот и буду помогать вам постить мемы в ваши каналы.\n"
        "Чтобы начать работу вам необходимо вызвать меню командой /menu и зарегистрироваться. Следующим шагом будет "
        "будет добавление бота в канал, в который вы хотите публиковать сообщения и привязка этого канала к вашему "
        "аккаунту. Боту в канале достаточно дать права на отправку сообщений."
    )
    await update.message.reply_text(text=start_text)


async def channel_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """При добавлении бота в новый канал, сохраняет его в БД, иначе обновляет информацию в БД о нем."""
    if update.my_chat_member.chat.type in Chat.CHANNEL:
        previous_status = update.my_chat_member.old_chat_member.status
        if previous_status in ChatMember.BANNED or previous_status in ChatMember.LEFT:
            channel = await base.channel_repository.get_channel(update.my_chat_member.chat.id)
            if channel:
                await services.update_channel(update.my_chat_member.chat, channel)
            else:
                await services.create_channel(update.my_chat_member.chat)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Парсит фото, видео и анимацию из полученного сообщения."""
    user = await base.user_repository.get_user(update.effective_user.id)
    if context.user_data.get(constants.STOP_FORWARD, None) or not user:
        return
    for i in user.channels:
        print(i)
    # try:
    #     user = await user_repository.get_user(update.effective_user.id)
    # except exc.NoResultFound:
    #     raise exc.NoResultFound
    # for channel in user.channels:
    #     if channel and channel.is_active is True:
    #         channel_id = channel.channel_id
    #         await services.posting_message(update.message, channel_id, context.bot)
