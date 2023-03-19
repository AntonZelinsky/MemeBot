from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import ContextTypes, ConversationHandler

from src import exceptions, services
from src.constants import callback_data, constants, states
from src.db import base


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Выводит главное меню при вызове команды /menu."""
    try:
        await base.user_repository.get(update.effective_user.id)
    except exceptions.UserNotFound:
        await update.message.reply_text(text="Вы не зарегистрированы. Для регистрации введите команду /register")
        return

    context.user_data[constants.STOP_FORWARD] = False
    buttons = [
        [InlineKeyboardButton("Привязать канал", callback_data=callback_data.CALLBACK_CALL_BINDING)],
        [InlineKeyboardButton("Подключенные каналы", callback_data=callback_data.CALLBACK_USER_CHANNELS)],
        [InlineKeyboardButton("Закрыть меню", callback_data=callback_data.CALLBACK_CLOSE_MENU)],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=keyboard)
    else:
        await update.message.reply_text(text="Стартовое меню", reply_markup=keyboard)
    return states.MAIN_MENU_STATE


async def call_binding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Вызывает функцию привязки канала и блокирует пересылку сообщений в каналы пользователя."""
    text = "Добавьте бот в ваш канал и перешлите любое сообщение из этого канала в этот чат"
    context.user_data[constants.STOP_FORWARD] = True
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.BINDING


async def binding_user_with_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Связывает аккаунт пользователя и канал, из которого переслали сообщение."""
    text = None
    channel_title = None

    try:
        channel_title = update.message.forward_from_chat.title
        channel = await base.channel_repository.get(update.message.forward_from_chat.id)
        user = await base.user_repository.get(update.effective_user.id)
        await services.user_is_admin_in_channel(update, context.bot)
        await services.create_bind(user.id, channel.id)
    except exceptions.ChannelNotFound:
        text = f"Канал '{channel_title}' не найден в БД. Добавьте бот в канал еще раз"
    except exceptions.ObjectAlreadyExists:
        text = f"Канал '{channel_title}' уже привязан к вашему аккаунту"
    except exceptions.UserNotAdminInChannel:
        text = f"Вы не являетесь администратором канала '{channel_title}'"
    except error.Forbidden:
        text = f"Бот заблокирован в канале '{channel_title}'"
    except AttributeError:
        text = "Сообщение не является репостом из другого канала"
    else:
        text = f"Вы привязали канал '{channel_title}'"
    finally:
        await update.message.reply_text(text=text)
        return await main_menu(update, context)


async def user_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Выводит меню с каналами, привязанными к аккаунту пользователя."""
    user = await base.user_repository.get(update.effective_user.id)
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
    return states.USER_CHANNELS_STATE


async def channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Выводит меню выбранного канала."""
    buttons = [
        [InlineKeyboardButton("Изменить описание", callback_data=callback_data.CALLBACK_EDIT_DESCRIPTION)],
        [InlineKeyboardButton("Назад", callback_data=callback_data.CALLBACK_BACK_TO_CHANNELS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=keyboard)
        if update.callback_query.data:
            channel_id = int(update.callback_query.data)
            channel = await base.channel_repository.get(channel_id)
            context.user_data[constants.CURRENT_CHANNEL] = channel
    else:
        await update.message.reply_text(text="Меню канала", reply_markup=keyboard)
    return states.CHANNEL_MENU_STATE


async def edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Кнопка для изменения текста сообщения в выбранном канале."""
    text = "Введите новый текст сообщения для канала"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.TYPING_DESCRIPTION


async def input_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обрабатывает введенный пользователем текст сообщения для канала."""
    new_description = update.message.text
    await services.change_bind_description(new_description, context.user_data)
    await update.message.reply_text(text=f"Описание изменено. Новое описание '{new_description}'")
    return await channel_menu(update, context)


async def close_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Закрывает меню."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Открыть меню можно командой /menu")
    return ConversationHandler.END
