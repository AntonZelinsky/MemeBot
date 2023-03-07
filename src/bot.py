from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src import handlers, menu_commands, settings
from src.constants import callback_data, states


def create_bot():
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    menu_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", menu_commands.start_menu, filters.ChatType.PRIVATE)],
        states={
            states.START_MENU_STATE: [
                CallbackQueryHandler(menu_commands.start_menu, pattern=callback_data.CALLBACK_START_MENU_COMMAND),
            ],
            states.MAIN_MENU_STATE: [
                CallbackQueryHandler(
                    menu_commands.bind_the_channel,
                    pattern=callback_data.CALLBACK_BIND_THE_CHANNEL_COMMAND,
                ),
                CallbackQueryHandler(menu_commands.my_channels, pattern=callback_data.CALLBACK_MY_CHANNELS_COMMAND),
                CallbackQueryHandler(menu_commands.close_menu, pattern=callback_data.CALLBACK_CLOSE_MENU_COMMAND),
            ],
            states.MY_CHANNELS_STATE: [
                CallbackQueryHandler(menu_commands.channel_menu, pattern=callback_data.CALLBACK_CHANNEL_MENU_COMMAND),
                CallbackQueryHandler(menu_commands.start_menu, pattern=callback_data.CALLBACK_BACK_TO_MAIN_COMMAND),
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
            states.TYPING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu_commands.edit_description),
            ],
            states.TYPING_BINDING_CHANNEL: [
                MessageHandler(filters.TEXT, menu_commands.type_channel_for_binding),
            ],
        },
        fallbacks=[
            CommandHandler("menu", menu_commands.start_menu),
        ],
    )
    application.add_handler(CommandHandler("start", handlers.start, filters.ChatType.PRIVATE))
    application.add_handler(menu_handler)
    application.add_handler(ChatMemberHandler(handlers.track_chats_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (filters.VIDEO | filters.PHOTO | filters.ANIMATION),
            handlers.forward_attachment_handler,
        ),
    )
    return application
