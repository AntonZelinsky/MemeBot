from warnings import filterwarnings

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.warnings import PTBUserWarning

from src import handlers, menu_commands, settings
from src.constants import callback_data, states

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


def create_bot():
    builder = Application.builder()
    builder.token(settings.BOT_TOKEN)
    builder.concurrent_updates(False)
    application = builder.build()
    menu_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", menu_commands.start_menu, filters.ChatType.PRIVATE)],
        states={
            states.START_MENU_STATE: [
                CallbackQueryHandler(menu_commands.start_menu, pattern=callback_data.CALLBACK_START_MENU),
            ],
            states.MAIN_MENU_STATE: [
                CallbackQueryHandler(menu_commands.register, pattern=callback_data.CALLBACK_REGISTER),
                CallbackQueryHandler(menu_commands.bind_the_channel, pattern=callback_data.CALLBACK_BIND_THE_CHANNEL),
                CallbackQueryHandler(menu_commands.my_channels, pattern=callback_data.CALLBACK_MY_CHANNELS),
                CallbackQueryHandler(menu_commands.close_menu, pattern=callback_data.CALLBACK_CLOSE_MENU),
            ],
            states.MY_CHANNELS_STATE: [
                CallbackQueryHandler(menu_commands.channel_menu, pattern=callback_data.CALLBACK_CHANNEL_MENU),
                CallbackQueryHandler(menu_commands.start_menu, pattern=callback_data.CALLBACK_BACK_TO_MAIN),
            ],
            states.CHANNEL_MENU_STATE: [
                CallbackQueryHandler(menu_commands.edit_description, pattern=callback_data.CALLBACK_EDIT_DESCRIPTION),
                CallbackQueryHandler(menu_commands.my_channels, pattern=callback_data.CALLBACK_BACK_TO_CHANNELS),
            ],
            states.BINDING_CHANNEL: [
                MessageHandler(filters.ALL, menu_commands.type_channel_for_binding),
            ],
            states.TYPING_DESCRIPTION: [
                MessageHandler(filters.TEXT, menu_commands.input_description),
            ],
        },
        fallbacks=[CommandHandler("menu", menu_commands.start_menu)],
    )
    application.add_handler(CommandHandler("start", handlers.start, filters.ChatType.PRIVATE))
    application.add_handler(menu_handler)
    application.add_handler(ChatMemberHandler(handlers.channel_chat_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (filters.VIDEO | filters.PHOTO | filters.ANIMATION),
            handlers.forward_attachment_handler,
        ),
    )
    return application
