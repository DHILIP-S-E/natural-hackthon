"""Database compatibility — Patch PostgreSQL types to work with SQLite.

Import this BEFORE any models to ensure compatibility.
When using SQLite, PostgreSQL-specific types are replaced with compatible alternatives.
"""
import sys
from app.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    import types
    from sqlalchemy import JSON, String, Text
    from sqlalchemy import Enum as _SAEnum

    # Create a fake postgresql.ARRAY that returns JSON
    class _FakeARRAY:
        """SQLite-compatible ARRAY replacement — stores as JSON."""
        def __init__(self, *args, **kwargs):
            pass

        def __class_getitem__(cls, item):
            return JSON

    # Create a fake JSONB that maps to JSON
    _FakeJSONB = JSON

    # Patch the postgresql dialects module so imports work
    pg_module = types.ModuleType("sqlalchemy.dialects.postgresql")
    pg_module.JSONB = JSON
    pg_module.ARRAY = _FakeARRAY
    sys.modules.setdefault("sqlalchemy.dialects.postgresql", pg_module)

    # Also patch Enum to use String for SQLite
    import sqlalchemy
    _original_enum = sqlalchemy.Enum

    class _SQLiteCompatEnum(_original_enum):
        """Enum that falls back to String(50) on SQLite."""
        def __init__(self, *args, **kwargs):
            # Remove PostgreSQL-specific kwargs
            kwargs.pop("create_type", None)
            super().__init__(*args, **kwargs)

    # Don't override the global Enum — models that need it will use SAEnum directly

    print("[DB_COMPAT] SQLite mode — PostgreSQL types patched")
