from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from src import services
from src.constants import callback_data, constants, states
from src.db import base, models

x = [
    {"название": "первое название", "что-то еще": "опять еще"},
    {"название": "второе название", "что-то еще": "опять еще"},
]


async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Начальное меню."""
    context.user_data[constants.STOP_FORWARD] = False
    register_button = [[InlineKeyboardButton("Зарегистрироваться", callback_data=callback_data.CALLBACK_REGISTER)]]
    bind_button = [[InlineKeyboardButton("Привязать канал", callback_data=callback_data.CALLBACK_BIND_THE_CHANNEL)]]
    channels_button = [[InlineKeyboardButton("Подключенные каналы", callback_data=callback_data.CALLBACK_MY_CHANNELS)]]
    buttons = [[InlineKeyboardButton("Закрыть меню", callback_data=callback_data.CALLBACK_CLOSE_MENU)]]

    user = await base.user_repository.get_user(update.effective_user.id)

    if not user:
        buttons = register_button + buttons
    else:
        buttons = bind_button + channels_button + buttons

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=keyboard)
    else:
        await update.message.reply_text(text="Стартовое меню", reply_markup=keyboard)

    return states.MAIN_MENU_STATE


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Регистрирует пользователя."""
    await services.create_user(update.effective_user)
    await update.callback_query.edit_message_text(text="Вы зарегистрированы.")
    return await start_menu(update, context)


async def bind_the_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Связывает канал и пользователя."""
    text = "Добавьте бот в ваш канал и перешлите любое сообщение из этого канала в чат бота."
    user_data = context.user_data
    user_data[constants.STOP_FORWARD] = True
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.BINDING_CHANNEL


async def type_channel_for_binding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user = await base.user_repository.get_user(update.effective_user.id)
    channel = await base.channel_repository.get_channel(update.message.forward_from_chat.id)
    # binding = await base.user_channel_repository.get_bind(user.id, channel.id)
    # if not binding:
    admins = await context.bot.get_chat_administrators(chat_id=update.message.forward_from_chat.id)
    for i in admins:
        if i.user.id == update.effective_user.id:
            new_bind = models.UserChannel.new_bind(user.id, channel.id)
            new_bind = await base.user_channel_repository.create(new_bind)

    await update.message.reply_text(text=f"Вы привязали канал '{update.message.forward_from_chat.title}'.")
    return await start_menu(update, context)


async def my_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    c_buttons = [[InlineKeyboardButton(i["название"], callback_data=callback_data.CALLBACK_CHANNEL_MENU)] for i in x]

    back_button = [[InlineKeyboardButton("Назад", callback_data=callback_data.CALLBACK_BACK_TO_MAIN)]]
    buttons = c_buttons + back_button
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="Список ваших каналов", reply_markup=keyboard)
    return states.MY_CHANNELS_STATE


async def channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    buttons = [
        [InlineKeyboardButton("Изменить описание", callback_data=callback_data.CALLBACK_EDIT_DESCRIPTION)],
        [InlineKeyboardButton("Выйти ботом из группы", callback_data=callback_data.CALLBACK_LEAVE_THE_CHANNEL)],
        [InlineKeyboardButton("Назад", callback_data=callback_data.CALLBACK_BACK_TO_CHANNELS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="Меню канала", reply_markup=keyboard)
    else:
        await update.message.reply_text(text="Меню канала", reply_markup=keyboard)
    return states.CHANNEL_MENU_STATE


async def leave_the_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Вы вышли из канала {}"
    await context.bot.leave_chat(chat_id=1001722199850)
    await update.callback_query.edit_message_text(text=text)
    return await my_channels(update, context)


async def edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Введите новое описание."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.TYPING_DESCRIPTION


async def input_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_data = context.user_data
    user = update.effective_user.id
    user_data[user] = update.message.text
    await update.message.reply_text(update.message.text)
    return await channel_menu(update, context)


async def close_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Открыть меню можно командой /menu")
    return ConversationHandler.END
