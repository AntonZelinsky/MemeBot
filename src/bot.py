from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src import menu_commands
from src.constants import callback_data, states
from src.handlers import forward_attachment_handler, track_chats_handler
from src.settings import BOT_TOKEN


def create_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    menu_handler = ConversationHandler(
        entry_points=[CommandHandler("start", menu_commands.start)],
        states={
            states.START_STATE: [CallbackQueryHandler(menu_commands.start, pattern="start")],
            states.MAIN_MENU_STATE: [
                CallbackQueryHandler(menu_commands.my_channels, pattern=callback_data.CALLBACK_MY_CHANNELS_COMMAND),
                CallbackQueryHandler(menu_commands.close_menu, pattern=callback_data.CALLBACK_CLOSE_MENU_COMMAND),
            ],
            states.MY_CHANNELS_STATE: [
                CallbackQueryHandler(menu_commands.channel_menu, pattern=callback_data.CALLBACK_CHANNEL_MENU_COMMAND),
                CallbackQueryHandler(menu_commands.start, pattern=callback_data.CALLBACK_BACK_TO_MAIN_COMMAND),
            ],
            states.CHANNEL_MENU_STATE: [
                CallbackQueryHandler(
                    menu_commands.ask_for_input,
                    pattern=callback_data.CALLBACK_EDIT_DESCRIPTION_COMMAND,
                ),
                CallbackQueryHandler(
                    menu_commands.leave_the_channel,
                    pattern=callback_data.CALLBACK_LEAVE_THE_CHANNEL_COMMAND,
                ),
                CallbackQueryHandler(
                    menu_commands.my_channels,
                    pattern=callback_data.CALLBACK_BACK_TO_CHANNELS_COMMAND,
                ),
            ],
            states.TYPING_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_commands.edit_description)],
        },
        fallbacks=[
            CommandHandler("start", menu_commands.start),
        ],
    )

    application.add_handler(menu_handler)
    application.add_handler(ChatMemberHandler(track_chats_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (filters.VIDEO | filters.PHOTO | filters.ANIMATION),
            forward_attachment_handler,
        ),
    )
    return application
