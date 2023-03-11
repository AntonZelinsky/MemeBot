from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from src import services
from src.constants import callback_data, constants, states
from src.db import base


async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Стартовое меню."""
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
    await update.callback_query.edit_message_text(text="Вы зарегистрированы")
    return await start_menu(update, context)


async def bind_the_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Кнопка для связывания канала и аккаунта пользователя."""
    text = "Добавьте бот в ваш канал и перешлите любое сообщение из этого канала в чат бота"
    context.user_data[constants.STOP_FORWARD] = True
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.BINDING_CHANNEL


async def type_channel_for_binding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Связывает аккаунт пользователя и канал."""
    channel = await base.channel_repository.get_channel(update.message.forward_from_chat.id)
    if not channel:
        return await start_menu(update, context)
    user = await base.user_repository.get_user(update.effective_user.id)
    bind = await base.bind_repository.get_bind(user.id, channel.id)
    if not bind:
        is_channel_admin = await services.check_user_is_admin(update, context.bot)
        if is_channel_admin:
            await services.create_bind(user.id, channel.id)
            await update.message.reply_text(text=f"Вы привязали канал '{update.message.forward_from_chat.title}'")
    return await start_menu(update, context)


async def my_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Меню каналов."""
    user = await base.user_repository.get_user(update.effective_user.id)
    context.user_data[constants.CURRENT_USER] = user
    channels_buttons = []
    for bind in user.channels:
        channels_buttons.append(
            [InlineKeyboardButton(bind.channel.title, callback_data=str(bind.channel.channel_id))],
        )
    back_button = [[InlineKeyboardButton("Назад", callback_data=callback_data.CALLBACK_BACK_TO_MAIN)]]
    buttons = channels_buttons + back_button
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="Список привязанных каналов", reply_markup=keyboard)
    return states.MY_CHANNELS_STATE


async def channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Меню канала."""
    buttons = [
        [InlineKeyboardButton("Изменить описание", callback_data=callback_data.CALLBACK_EDIT_DESCRIPTION)],
        [InlineKeyboardButton("Назад", callback_data=callback_data.CALLBACK_BACK_TO_CHANNELS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=keyboard)
        try:
            channel_id = int(update.callback_query.data)
            channel = await base.channel_repository.get_channel(channel_id)
            context.user_data[constants.CURRENT_CHANNEL] = channel
        except ValueError:
            pass
    else:
        await update.message.reply_text(text="Меню канала", reply_markup=keyboard)
    return states.CHANNEL_MENU_STATE


async def edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Кнопка для изменения описания сообщения для выбранного канала."""
    text = "Введите новое описание для канала"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.TYPING_DESCRIPTION


async def input_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обрабатывает введенное пользователем новое описание для канала."""
    await services.change_bind_description(update, context.user_data)
    await update.message.reply_text(text="Описание изменено")
    return await channel_menu(update, context)


async def close_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Закрывает меню."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Открыть меню можно командой /menu")
    return ConversationHandler.END
