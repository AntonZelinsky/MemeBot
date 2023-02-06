from telegram.ext import ApplicationBuilder, ChatMemberHandler, MessageHandler, filters

from src.handlers import forward_to_your_group, track_chats
from src.settings import BOT_TOKEN


def create_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.ALL, forward_to_your_group))
    return application
