from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.models import Channel, User
from src.settings import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Создает и обновляет объект в БД."""

    def __init__(self, model: T, session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def create(self, new_data: T) -> T:
        """Создает объект текущей модели и возвращает его."""
        self._session.add(new_data)
        await self._session.commit()
        await self._session.refresh(new_data)
        await self._session.close()
        return new_data

    async def update(self, object_id: int, update_data: T) -> T:
        """Обновляет объект текущей модели и возвращает его."""
        update_data.id = object_id
        update_data = await self._session.merge(update_data)
        await self._session.commit()
        await self._session.close()
        return update_data


class UserRepository(BaseRepository[User]):
    """Класс для работы с моделью User в БД."""

    def __init__(self) -> None:
        super().__init__(User, async_session())

    async def get_user(self, account_id: int) -> User:
        """Возвращает объект User из БД по его account_id."""
        user = await self._session.scalars(select(self._model).where(self._model.account_id == account_id))
        await self._session.close()
        return user.one()


class ChannelRepository(BaseRepository[Channel]):
    """Класс для работы с моделью Channel в БД."""

    def __init__(self) -> None:
        super().__init__(Channel, async_session())

    async def get_channel(self, channel_id: int) -> Channel:
        """Возвращает объект Channel из БД по его channel_id."""
        channel = await self._session.scalars(
            select(self._model).where(self._model.channel_id == channel_id).where(self._model.is_active),
        )
        await self._session.close()
        return channel.one()


user_manager = UserRepository()
channel_manager = ChannelRepository()
