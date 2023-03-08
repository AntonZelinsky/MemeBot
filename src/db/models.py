from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовая модель."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False, onupdate=func.now())


class UserChannel(Base):
    """Модель связей пользователей и каналов."""

    __tablename__ = "userchannel"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channel.id"), primary_key=True)
    description: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(default=True)  # ???

    @classmethod
    def from_parse(cls, user, channel) -> "UserChannel":
        ...

    def __repr__(self) -> str:
        return (
            f"UserChannel("
            f"user_id={self.user_id!r}, "
            f"channel_id={self.channel_id!r}, "
            f"description={self.description!r}, "
            f"is_active={self.is_active!r})"  # ???
        )


class User(Base):
    """Модель пользователя."""

    __tablename__ = "user"
    account_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    username: Mapped[Optional[str]]
    channels: Mapped[List["UserChannel"]] = relationship(
        backref="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    @classmethod
    def from_parse(cls, user_data: dict) -> "User":
        """Парсит данные из data в модель User."""
        return cls(
            account_id=user_data["id"],
            first_name=user_data["first_name"],
            last_name=user_data.get("last_name", None),
            username=user_data.get("username", None),
        )

    def __repr__(self) -> str:
        return (
            f"User("
            f"id={self.id!r}, "
            f"account_id={self.account_id!r}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"username={self.username!r}, "
            f"is_active={self.is_active!r})"
        )


class Channel(Base):
    """Модель канала."""

    __tablename__ = "channel"
    channel_id: Mapped[BigInteger] = mapped_column(unique=True)
    title: Mapped[str]
    username: Mapped[Optional[str]]
    # invited_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    users: Mapped[List["UserChannel"]] = relationship(
        backref="channels",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    @classmethod
    def from_parse(cls, channel_data: dict) -> "Channel":
        """Парсит данные из data в модель User."""
        return cls(
            channel_id=channel_data["id"],
            title=channel_data["title"],
            username=channel_data.get("username", None),
            # invited_user_id=user_id,
        )

    def __repr__(self) -> str:
        return (
            f"Channel("
            f"id={self.id!r}, "
            f"channel_id={self.channel_id!r}, "
            f"title={self.title!r}, "
            f"username={self.username}, "
            # f"text_message={self.text_message}"
            # f"invited_user_id={self.invited_user_id!r}, "
            f"is_active={self.is_active!r})"
        )
