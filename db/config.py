# db/config.py
from __future__ import annotations

import datetime
from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

from data.config import PostgresSettings

psql = PostgresSettings()

engine: Engine = create_engine(psql.sync_connector, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime.datetime:
    # naive utc vaqt (Django default timezone bo'lmasa ham ishlaydi)
    return datetime.datetime.utcnow()


class BaseModel(Base):
    """
    Django BaseModel kabi:
    - created_at: auto_now_add -> python default=utcnow
    - updated_at: auto_now -> python default=utcnow + onupdate=utcnow
    - uuid: default uuid4, unique
    - is_active: default True
    """
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)

    uuid: Mapped[UUID] = mapped_column(
        "uuid",
        PG_UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )

    # ✅ DB defaultga bog'lanmaymiz, Python o'zi to'ldiradi (Django kabi)
    created_at: Mapped[datetime.datetime] = mapped_column(
        "created_at",
        DateTime(timezone=False),
        default=utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        "updated_at",
        DateTime(timezone=False),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        "is_active",
        Boolean,
        default=True,
        nullable=False,
    )

    @property
    def created_at_utc(self) -> datetime.datetime | None:
        if self.created_at:
            return self.created_at + datetime.timedelta(hours=5)
        return None

    @property
    def updated_at_utc(self) -> datetime.datetime | None:
        if self.updated_at:
            return self.updated_at + datetime.timedelta(hours=5)
        return None