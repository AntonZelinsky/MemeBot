from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовая модель."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False, onupdate=func.now())


class User(Base):
    """Модель пользователя."""

    __tablename__ = "user"
    account_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    username: Mapped[Optional[str]]
    channels: Mapped[List["Channel"]] = relationship(
        back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return (
            f"User: "
            f"id={self.id!r}, "
            f"account_id={self.account_id!r}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"username={self.username!r}, "
            f"is_active={self.is_active!r}"
        )


class Channel(Base):
    """Модель канала."""

    __tablename__ = "channel"
    channel_id: Mapped[int]
    title: Mapped[str]
    username: Mapped[Optional[str]]
    invited_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="channels")
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return (
            f"Channel: "
            f"id={self.id!r}, "
            f"channel_id={self.channel_id!r}, "
            f"title={self.title!r}, "
            f"invited_user_id={self.invited_user_id!r}, "
            f"is_active={self.is_active!r}"
        )
