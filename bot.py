from environs import Env
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler
)

env = Env()
env.read_env()

MY_ID = env("MY_ID")
GROUP_ID = env("GROUP_ID")
DESCRIPTION = env("DESCRIPTION")
BOT_TOKEN = env("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Печатает id твоего профиля при запуске бота."""
    text = f"Ваш ID: {update.effective_chat.id}, добавьте его в переменную MY_ID"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """В режиме реального времени выводит название и номер группы, в которую добавляют бота с правами админа."""
    if update.my_chat_member.new_chat_member.status == 'administrator':
        text = (f"Группа '{update.my_chat_member.chat.title}' ID: {update.my_chat_member.chat.id}, "
               f"добавьте его в переменную GROUP_ID")
        await context.bot.send_message(chat_id=update.my_chat_member.from_user.id, text=text)


async def forward_to_your_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Публикует фото, анимацию, аудио и документы в группу из переменной group_chat."""
    if MY_ID is None or GROUP_ID is None:
        text = "Заполните переменные MY_ID и GROUP_ID"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    if MY_ID != update.effective_chat.id:
        text = "Ваш id не соответствует MY_ID"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    if update.message.photo:
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[0].file_id,
            caption=DESCRIPTION
        )
    elif update.message.animation:
        await context.bot.send_animation(
            chat_id=GROUP_ID,
            animation=update.message.animation.file_id,
            caption=DESCRIPTION
        )
    elif update.message.audio:
        await context.bot.send_audio(
            chat_id=GROUP_ID,
            audio=update.message.audio.file_id,
            caption=DESCRIPTION
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=GROUP_ID,
            document=update.message.document.file_id,
            caption=DESCRIPTION
        )
    elif update.message.video:
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id,
            caption=DESCRIPTION
        )


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.ALL, forward_to_your_group))
    application.run_polling()
