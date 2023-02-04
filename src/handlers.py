from telegram import Chat, ChatMember, Update
from telegram.ext import ContextTypes

from src import services
from src.db import channel_crud, get_async_session, user_crud
from src.settings import DESCRIPTION


async def save_or_update_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляем либо обновляем профиль пользователя в БД."""
    current_user_data = services.user_parser(update.effective_chat)
    get_session = get_async_session()
    session = await get_session.__anext__()
    user_db = await user_crud.get_user(current_user_data["account_id"], session)
    if user_db is None:
        await user_crud.create(current_user_data, session)
    else:
        await user_crud.update(user_db, current_user_data, session)
        await services.activate_user(account_id=current_user_data["account_id"], session=session)


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """В режиме реального времени доступ бота к чатам."""
    chat = update.effective_chat
    my_chat = update.my_chat_member
    account_id = my_chat.from_user.id
    get_session = get_async_session()
    session = await get_session.__anext__()
    # Отслеживаем блокировку чата пользователя и деактивируем его профиль
    if chat.type in Chat.PRIVATE and my_chat.new_chat_member.status in ChatMember.BANNED:
        await services.activate_user(account_id=account_id, session=session, status=False)
    # Отслеживаем действия в чатах каналов и добавляем канал в базу, либо его деактивируем
    if chat.type in Chat.CHANNEL:
        if (
            my_chat.new_chat_member.status in ChatMember.ADMINISTRATOR
            and my_chat.old_chat_member.status not in ChatMember.ADMINISTRATOR
        ):
            user_db = await user_crud.get_user(account_id, session)
            current_channel_data = services.channel_parser(my_chat.chat, user_db)
            await channel_crud.create(current_channel_data, session)
            text = f"Бот добавлен в канал '{my_chat.chat.title}'"
            await context.bot.send_message(chat_id=account_id, text=text)
        elif my_chat.new_chat_member.status in ChatMember.ADMINISTRATOR:
            text = f"У бота в канале '{my_chat.chat.title}' изменены права"
            await context.bot.send_message(chat_id=account_id, text=text)
        # При удалении бота из канала деактивируем чат в базе
        else:
            channel_db = await services.deactivate_channel(my_chat.chat.id, session)
            if channel_db.user.is_active:
                text = f"Бот удален из канала '{my_chat.chat.title}'"
                await context.bot.send_message(chat_id=channel_db.user.account_id, text=text)


async def forward_to_your_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Публикует фото, анимацию, аудио и документы в группу из переменной group_chat."""
    get_session = get_async_session()
    session = await get_session.__anext__()
    user_db = await user_crud.get_user(update.effective_user.id, session)
    channel_db = await channel_crud.get_channel_by_user(user_db, session)
    if update.message.photo:
        await context.bot.send_photo(
            chat_id=channel_db.channel_id, photo=update.message.photo[0].file_id, caption=DESCRIPTION
        )
    elif update.message.animation:
        await context.bot.send_animation(
            chat_id=channel_db.channel_id,
            animation=update.message.animation.file_id,
            caption=DESCRIPTION,
        )
    elif update.message.audio:
        await context.bot.send_audio(
            chat_id=channel_db.channel_id, audio=update.message.audio.file_id, caption=DESCRIPTION
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=channel_db.channel_id,
            document=update.message.document.file_id,
            caption=DESCRIPTION,
        )
    elif update.message.video:
        await context.bot.send_video(
            chat_id=channel_db.channel_id, video=update.message.video.file_id, caption=DESCRIPTION
        )
