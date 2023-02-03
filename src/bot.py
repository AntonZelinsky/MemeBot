from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.handlers import forward_to_your_group, save_or_update_user, track_chats
from src.settings import BOT_TOKEN


def create_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", save_or_update_user))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.ALL, forward_to_your_group))
    return application
