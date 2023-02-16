from typing import Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.models import Channel, User
from src.settings import DATABASE_URL

DatabaseModel = TypeVar("DatabaseModel")


class BaseCRUD:
    def __init__(self, model):
        self._model = model

    async def create(self, new_data: DatabaseModel, session: AsyncSession):
        """Создает объект текущей модели и возвращает его."""
        session.add(new_data)
        await session.commit()
        await session.refresh(new_data)
        return new_data

    async def update(self, object_id: int, update_data: DatabaseModel, session: AsyncSession) -> DatabaseModel:
        """Обновляет объект текущей модели и возвращает его."""
        update_data.id = object_id
        update_data = await session.merge(update_data)
        await session.commit()
        return update_data


class UserCRUD(BaseCRUD):
    async def get_user(self, account_id: int, session: AsyncSession) -> Optional[User]:
        """Возвращает объект User из БД по его account_id."""
        user = await session.execute(select(self._model).where(self._model.account_id == account_id))
        return user.scalars().first()


class ChannelCRUD(BaseCRUD):
    async def get_channel(self, channel_id: int, session: AsyncSession) -> Optional[Channel]:
        """Возвращает объект Channel из БД по его channel_id."""
        channel = await session.execute(
            select(self._model).where(self._model.channel_id == channel_id).where(self._model.is_active == True)
        )
        return channel.scalars().first()


engine = create_async_engine(DATABASE_URL, echo=False)


async def get_async_session() -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


user_crud = UserCRUD(User)
channel_crud = ChannelCRUD(Channel)
