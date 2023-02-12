from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Chat, ChatMember, ChatMemberUpdated, Message, Update
from telegram.ext import ContextTypes

from src import services
from src.db.crud import channel_crud, get_async_session, user_crud
from src.settings import DESCRIPTION


async def personal_chat_handler(my_chat_member: ChatMemberUpdated, current_status: str, session: AsyncSession):
    """Добавляет и изменяет информацию в БД о пользователях бота."""
    account_id = my_chat_member.from_user.id
    current_user_data = services.user_parser(my_chat_member.from_user)
    user_db = await user_crud.get_user(account_id, session)
    if user_db:
        user_id = user_db.id
        await user_crud.update(user_id, current_user_data, session)
    else:
        user_id = await user_crud.create(current_user_data, session)

    if current_status in ChatMember.BANNED:
        await services.activate_user(user_id=user_id, session=session, status=False)
    elif current_status in ChatMember.MEMBER:
        await services.activate_user(user_id=user_id, session=session)
    return user_id


async def channel_chat_handler(
    my_chat: ChatMemberUpdated,
    current_status: str,
    previous_status: str,
    session: AsyncSession,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Добавляет и изменяет информацию в БД о доступных боту каналах."""
    message = None

    if current_status in ChatMember.ADMINISTRATOR and current_status != previous_status:
        user_id = await personal_chat_handler(my_chat, current_status, session)
        current_channel_data = services.channel_parser(my_chat.chat, user_id)
        await channel_crud.create(current_channel_data, session)
        text = f"Бот добавлен в канал '{my_chat.chat.title}',"
        rights_text = services.check_bot_privileges(my_chat.new_chat_member)
        message = text + rights_text

    elif current_status == previous_status:
        text = f"У бота в канале '{my_chat.chat.title}' изменены права,"
        rights_text = services.check_bot_privileges(my_chat.new_chat_member)
        message = text + rights_text

    channel_db = await channel_crud.get_channel(my_chat.chat.id, session)

    if current_status in [ChatMember.BANNED, ChatMember.LEFT]:
        if channel_db:
            await services.deactivate_channel(channel_db.id, session)
            message = f"Бот удален из канала '{my_chat.chat.title}'"

    if channel_db and channel_db.user.is_active:
        await context.bot.send_message(chat_id=channel_db.user.account_id, text=message)


async def track_chats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверяет чаты бота."""
    get_session = get_async_session()
    session = await get_session.__anext__()

    my_chat = update.my_chat_member
    current_status = my_chat.new_chat_member.status
    previous_status = my_chat.old_chat_member.status

    if my_chat.chat.type in Chat.PRIVATE:
        if current_status != previous_status:
            await personal_chat_handler(my_chat, current_status, session)

    if my_chat.chat.type in Chat.CHANNEL:
        await channel_chat_handler(my_chat, current_status, previous_status, session, context)


async def posting_message_handler(message: Message, channel_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Публикует вложение из сообщения пользователя в канал."""
    if message.animation:
        await context.bot.send_animation(
            chat_id=channel_id,
            animation=message.animation.file_id,
            caption=DESCRIPTION,
        )
    elif message.photo:
        await context.bot.send_photo(chat_id=channel_id, photo=message.photo[0].file_id, caption=DESCRIPTION)
    else:
        await context.bot.send_video(chat_id=channel_id, video=message.video.file_id, caption=DESCRIPTION)


async def forward_attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Парсит фото, видео и анимацию из сообщения от пользователя."""
    get_session = get_async_session()
    session = await get_session.__anext__()
    user_db = await user_crud.get_user(update.effective_user.id, session)
    for channel in user_db.channels:
        if channel and channel.is_active is True:
            channel_id = channel.channel_id
            await posting_message_handler(update.message, channel_id, context)
