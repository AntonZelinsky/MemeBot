from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler
)

# Номер твоего профиля, используется для ограничения постинга только с твоего ака
MY_ID = None
# Номер группы в которую надо постить, начинается со знака '-' (число)
GROUP_ID = None
# Описание к публикуемым фото/видео и тд
DESCRIBE = ""
# Токен бота
BOT_TOKEN = ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит стартовое приветствие."""
    text = """
    Иструкция для бота:
    1) Запишите в переменную MY_ID номер вашего чата (в сообщении ниже)
    2) Заполните переменную DESCRIBE, она содержит подпись к вашим сообщениям.
    3) Добавьте бота в вашу группу, разрешив публиковать посты
    4) Заполните переменную GROUP_ID номером чата группы (придет в чат бота после добавления бота в группу)
    5) Удалите бота из группы, перезапустите бота с заполненными данными, перезагрузте бота, добавьте бота в нужную группу
    """
    # Печатает стартовое приветствие
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    # Печатает id твоего профиля
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_chat.id)


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """В режиме реального времени выводит название и номер группы, в которую добавляют бота с правами админа."""
    # Проверяет статус чата бота в режиме online, если появляется новый чат со статусом administrator,
    # в который ТЫ его добавил, то печатает id и название этого чата (такие чаты только в группе)
    if update.my_chat_member.new_chat_member.status == 'administrator':
        text = f"Группа '{update.my_chat_member.chat.title}' ID: {update.my_chat_member.chat.id}"
        await context.bot.send_message(chat_id=update.my_chat_member.from_user.id, text=text)


async def forward_to_your_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Публикует фото, анимацию, аудио и документы в группу из переменной group_chat."""
    # Проверяет заполнены ли данные
    if MY_ID is None or GROUP_ID is None:
        text = "Заполните переменные MY_ID и GROUP_ID"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    # Та самая проверка на ID профиля, чтобы посты от других не постились в твою группу
    if MY_ID != update.effective_chat.id:
        text = "Ваш id не соответствует MY_ID"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    # Проверка на тип входящего сообщения к боту: фото/анимация/аудио/документ/видео и
    # отправка этого вложения в чат группы GROUP_ID с подписью DESCRIBE
    if update.message.photo:
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[0].file_id,
            caption=DESCRIBE
        )
    elif update.message.animation:
        await context.bot.send_animation(
            chat_id=GROUP_ID,
            animation=update.message.animation.file_id,
            caption=DESCRIBE
        )
    elif update.message.audio:
        await context.bot.send_audio(
            chat_id=GROUP_ID,
            audio=update.message.audio.file_id,
            caption=DESCRIBE
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=GROUP_ID,
            document=update.message.document.file_id,
            caption=DESCRIBE
        )
    elif update.message.video:
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id,
            caption=DESCRIBE
        )


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    # Стартовое приветствие с инструкцией и выводом твоего id, после заполнения переменных можно отключить/удалить
    application.add_handler(CommandHandler("start", start))
    # Выводит в реальном времени информацию группы, в которую ТЫ добавил бота, после заполнения данных можно
    # отключить/удалить
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    # То самое что тебе надо, тупо проверяет тип пришедших боту данных, чтобы знать где взять id вложения и
    # отправляет в нужную тебе группу сообщение с этим вложением и подписью из переменной DESCRIBE
    application.add_handler(MessageHandler(filters.ALL, forward_to_your_group))
    application.run_polling()
