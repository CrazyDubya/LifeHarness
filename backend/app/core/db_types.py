"""Database-agnostic column type helpers for SQLite/PostgreSQL compatibility"""
from sqlalchemy import JSON, Text, String, CHAR
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, JSONB as PG_JSONB, UUID as PG_UUID
from sqlalchemy.types import TypeDecorator
from uuid import UUID as PyUUID
from app.core.config import settings


def is_sqlite():
    """Check if we're using SQLite"""
    return "sqlite" in settings.DATABASE_URL.lower()


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, PyUUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, PyUUID):
                return value
            return PyUUID(value)


def UUIDType():
    """Return UUID type that works with both PostgreSQL and SQLite"""
    return GUID


def JSONBType():
    """Return JSONB for PostgreSQL, JSON for SQLite"""
    if is_sqlite():
        return JSON
    return PG_JSONB


def ArrayType(item_type=Text):
    """Return ARRAY for PostgreSQL, JSON for SQLite

    Note: When using SQLite, the application must handle list serialization.
    Arrays should be stored as JSON arrays and properly serialized/deserialized.
    """
    if is_sqlite():
        # SQLite doesn't support ARRAY, use JSON instead
        return JSON
    return PG_ARRAY(item_type)
