"""AURA Database — Async SQLAlchemy 2.0 setup with SQLite/PostgreSQL support."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import MetaData, func, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime

from app.config import settings

# Naming convention for constraints (Alembic-friendly)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

if not is_sqlite:
    engine_kwargs["pool_size"] = 30
    engine_kwargs["max_overflow"] = 20

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Enable foreign keys for SQLite
if is_sqlite:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    metadata = metadata


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )


class SoftDeleteMixin:
    """Mixin that adds is_deleted and deleted_at columns."""
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def generate_uuid() -> str:
    return str(uuid.uuid4())


def enum_val(v):
    """Safely get enum value — works whether v is an Enum or already a string."""
    if v is None:
        return None
    return v.value if hasattr(v, 'value') else str(v)


# ── Cross-database type helpers ──
# SQLite doesn't support ARRAY or JSONB, so we use JSON for both.
from sqlalchemy import JSON, Text
from sqlalchemy.types import TypeDecorator
import json

if is_sqlite:
    # On SQLite: ARRAY → JSON, JSONB → JSON, Enum → String
    FlexibleJSON = JSON
    FlexibleARRAY = JSON  # Store arrays as JSON

    class FlexibleEnum(TypeDecorator):
        """Store enum as string in SQLite."""
        impl = Text
        cache_ok = True

        def __init__(self, enum_class, **kw):
            super().__init__(**kw)
            self.enum_class = enum_class

        def process_bind_param(self, value, dialect):
            if value is None:
                return None
            return value.value if hasattr(value, 'value') else str(value)

        def process_result_value(self, value, dialect):
            if value is None:
                return None
            try:
                return self.enum_class(value)
            except (ValueError, KeyError):
                return value
else:
    from sqlalchemy.dialects.postgresql import JSONB, ARRAY as PG_ARRAY
    from sqlalchemy import Enum as SAEnum
    FlexibleJSON = JSONB
    FlexibleARRAY = None  # Use PG_ARRAY directly in models
    FlexibleEnum = None  # Use SAEnum directly in models


async def get_db() -> AsyncSession:
    """Dependency — yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
