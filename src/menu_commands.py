from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.constants import callback_data, states

x = [
    {"название": "первое название", "что-то еще": "опять еще"},
    {"название": "второе название", "что-то еще": "опять еще"},
]


async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # start_text = (
    #     "Привет. Я — Мем бот и буду помогать вам постить мемы на ваши каналы.\n"
    #     "Чтобы начать работу, нужно добавить каналы на которые вы хотите  постить сообщения.\n"
    #     "Для того чтобы связать ваш канал с вашей учётной записью, добавьте этот бот в администраторы канала и "
    #     "перешлите с канала сообщение сюда. Если и вы и бот являетесь администраторами канала, то будет создана "
    #     "связь и вы сможете постить сообщения туда. Боту на канале достаточно дать права на отправку сообщений."
    # )
    # print(f"menu up={update}")
    buttons = [
        [
            InlineKeyboardButton("Связать новый канал", callback_data=callback_data.CALLBACK_BIND_THE_CHANNEL_COMMAND),
        ],
        [
            InlineKeyboardButton("Подключенные каналы", callback_data=callback_data.CALLBACK_MY_CHANNELS_COMMAND),
        ],
        [
            InlineKeyboardButton("Закрыть меню", callback_data=callback_data.CALLBACK_CLOSE_MENU_COMMAND),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="Стартовое меню", reply_markup=keyboard)
    else:
        # await update.message.reply_text(start_text)
        await update.message.reply_text("Стартовое меню", reply_markup=keyboard)

    return states.MAIN_MENU_STATE


async def bind_the_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Для привязки канала в котором уже есть бот введите сокрещение канала в виде @channel."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.TYPING_BINDING_CHANNEL


async def type_channel_for_binding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_data = context.user_data
    user = update.effective_user.id
    user_data[user] = update.message.text
    await update.message.reply_text(update.message.text)
    return await start_menu(update, context)


async def my_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()
    channels_buttons = []
    for i in x:
        channels_buttons.append(
            [InlineKeyboardButton(i["название"], callback_data=callback_data.CALLBACK_CHANNEL_MENU_COMMAND)],
        )
    back_button = [[InlineKeyboardButton("Назад", callback_data=callback_data.CALLBACK_BACK_TO_MAIN_COMMAND)]]
    buttons = channels_buttons + back_button
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text="Список ваших каналов", reply_markup=keyboard)
    return states.MY_CHANNELS_STATE


async def channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    buttons = [
        [InlineKeyboardButton("Изменить описание", callback_data=callback_data.CALLBACK_EDIT_DESCRIPTION_COMMAND)],
        [InlineKeyboardButton("Выйти ботом из группы", callback_data=callback_data.CALLBACK_LEAVE_THE_CHANNEL_COMMAND)],
        [InlineKeyboardButton("Назад", callback_data=callback_data.CALLBACK_BACK_TO_CHANNELS_COMMAND)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="Меню канала", reply_markup=keyboard)
    else:
        await update.message.reply_text("Меню канала", reply_markup=keyboard)
    return states.CHANNEL_MENU_STATE


async def left_channel(context, id) -> None:
    await context.bot.leave_chat(chat_id=id)


async def leave_the_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await left_channel(context, -1001722199850)
    return await my_channels(update, context)


async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Введите новое описание."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)
    return states.TYPING_DESCRIPTION


async def edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
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
