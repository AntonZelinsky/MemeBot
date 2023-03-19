from telegram import Chat, ChatMember, Update, error
from telegram.ext import CallbackContext, ContextTypes

from src import exceptions, services
from src.constants import constants
from src.db import base


async def start_message_handler(update: Update, context: CallbackContext) -> None:
    """Выводит приветственное сообщение при вызове команды /start."""
    start_text = (
        "Привет. Я — Мем бот и буду помогать вам постить мемы в ваши каналы.\n"
        "Чтобы начать работу вам необходимо зарегистрироваться в боте, сделать это можно вызвав команду /register. \n"
        "Как только вы зарегистрируетесь, вы сможете вызвать меню бота командой /menu. Следующим шагом будет "
        "будет добавление бота в канал, в который вы хотите публиковать сообщения и привязка этого канала к вашему "
        "аккаунту. Боту в канале достаточно дать права на отправку сообщений."
    )
    await update.message.reply_text(text=start_text)


async def user_register_handler(update: Update, context: CallbackContext) -> None:
    """Создает пользователя в БД при вызове команды /register."""
    message = ""
    try:
        await services.create_user(update.effective_user)
    except exceptions.ObjectAlreadyExists:
        message = "Вы уже зарегистрированы. Для вызова меню используйте команду /menu"
    else:
        message = "Вы успешно зарегистрированы. Для вызова меню используйте команду /menu"
    finally:
        await update.message.reply_text(text=message)


async def channel_register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """При добавлении бота в новый канал, сохраняет его в БД."""
    my_chat = update.my_chat_member
    if my_chat.chat.type in Chat.CHANNEL and my_chat.old_chat_member.status in [ChatMember.BANNED, ChatMember.LEFT]:
        try:
            await services.create_channel(update.my_chat_member.chat)
        except exceptions.ObjectAlreadyExists:
            return


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Парсит фото, видео и анимацию из полученного сообщения и пересылает в каналы пользователя."""
    if context.user_data.get(constants.STOP_FORWARD, False):
        return

    try:
        user = await base.user_repository.get(update.effective_user.id)
    except exceptions.UserNotFound:
        await update.message.reply_text(text="Прежде чем пользоваться ботом, вы должны зарегистрироваться")
        return

    for bind in user.channels:
        try:
            await services.posting_message(bind, update.message, context.bot)
        except error.Forbidden:
            await update.message.reply_text(
                text=f"Невозможно отправить сообщение в канал '{bind.channel.title}'. Бот удален из канала",
            )
        except error.BadRequest:
            await update.message.reply_text(
                text=f"Невозможно отправить сообщение в канал '{bind.channel.title}'. У бота недостаточно прав",
            )
