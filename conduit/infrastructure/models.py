from datetime import datetime
from functools import partial

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


relationship = partial(relationship, lazy="raise")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    bio: Mapped[str]
    image_url: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime] = mapped_column(nullable=True)


class FollowerFollowingMap(Base):
    __tablename__ = "follower_following_map"

    # "Followers" are the users who follow you.
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True, nullable=False
    )
    # "Following" are the users who you follow.
    following_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True, nullable=False
    )
    created_at: Mapped[datetime]
