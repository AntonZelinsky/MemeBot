from typing import Optional

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from src.db.models import Channel, User
from src.settings import DATABASE_URL


class BaseCRUD:
    def __init__(self, model):
        self._model = model

    async def create(self, new_data: dict, session: AsyncSession):
        """Создает объект текущей модели и возвращает его id."""
        obj_id = await session.execute(insert(self._model).values(new_data).returning(self._model.id))
        await session.commit()
        return obj_id.scalars().first()

    async def update(self, object_id: int, update_data: dict, session: AsyncSession):
        """Обновляет объект текущей модели."""
        await session.execute(update(self._model).where(self._model.id == object_id).values(update_data))
        await session.commit()


class UserCRUD(BaseCRUD):
    async def get_user(self, account_id: int, session: AsyncSession) -> Optional[User]:
        """Возвращает объект User из БД по его account_id."""
        user = await session.execute(
            select(self._model).where(self._model.account_id == account_id).options(selectinload(self._model.channels))
        )
        return user.scalars().first()


class ChannelCRUD(BaseCRUD):
    async def get_channel(self, channel_id: int, session: AsyncSession) -> Optional[User]:
        """Возвращает объект Channel из БД по его channel_id."""
        channel = await session.execute(
            select(self._model)
            .where(self._model.channel_id == channel_id)
            .where(self._model.is_active == True)
            .options(selectinload(self._model.user))
        )
        return channel.scalars().first()


engine = create_async_engine(DATABASE_URL, echo=False)


async def get_async_session() -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


user_crud = UserCRUD(User)
channel_crud = ChannelCRUD(Channel)
