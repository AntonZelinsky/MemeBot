from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship


@as_declarative()
class Base:
    """Базовая модель."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.current_timestamp(),
        nullable=False,
        onupdate=func.current_timestamp(),
    )


class User(Base):
    """Модель пользователя."""

    account_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    username: Mapped[Optional[str]]
    channel: Mapped[List["Channel"]] = relationship(back_populates="user")
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
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

    channel_id: Mapped[int]
    title: Mapped[str]
    username: Mapped[Optional[str]]
    invited_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="channel")
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return (
            f"Channel: "
            f"id={self.id!r}, "
            f"channel_id={self.channel_id!r}, "
            f"title={self.title!r}, "
            f"invited_user_id={self.invited_user_id!r}, "
            f"is_active={self.is_active!r}"
        )
