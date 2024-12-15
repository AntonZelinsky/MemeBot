from telegram import Chat, ChatMember, Update, error
from telegram.ext import CallbackContext, ContextTypes

from src import services
from src.constants import constants
from src.db import base


async def start_message_handler(update: Update, context: CallbackContext) -> None:
    """Выводит приветственное сообщение при вызове команды /start и регистрирует пользователя."""
    start_text = (
        "Привет. Я — Мем бот и буду помогать вам постить мемы в ваши каналы.\n"
        "Перед началом работы с ботом, вам необходимо добавить бота в ваши каналы и через меню привязать каналы "
        "к вашему аккаунту. Вызвать меню бота можно командой /menu"
    )
    await services.create_user(update.effective_user)
    # Разрешает пересылать пользователю сообщения в каналы
    context.user_data[constants.STOP_FORWARD] = False
    await update.message.reply_text(text=start_text)


async def channel_register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """При добавлении бота в канал сохраняет его в БД. Если такой канал уже есть в БД - обрабатывается исключение."""
    my_chat = update.my_chat_member
    if my_chat.chat.type in Chat.CHANNEL and my_chat.old_chat_member.status in [ChatMember.BANNED, ChatMember.LEFT]:
        await services.create_channel(update.my_chat_member.chat)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Перебирает каналы пользователя и вызывает функцию публикации вложений в эти каналы."""
    if context.user_data.get(constants.STOP_FORWARD, False):
        return
    user = await base.user_repository.get(update.effective_user.id)
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
