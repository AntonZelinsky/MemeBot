from telegram.ext import ApplicationBuilder, ChatMemberHandler, MessageHandler, filters

from src.handlers import forward_attachment_handler, track_chats_handler
from src.settings import BOT_TOKEN


def create_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(ChatMemberHandler(track_chats_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (filters.VIDEO | filters.PHOTO | filters.ANIMATION), forward_attachment_handler
        )
    )
    return application
